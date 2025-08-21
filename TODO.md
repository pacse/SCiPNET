# What to work on from ChatGPT

# Immediate, concrete problems to fix (by file)

## `client.py` — issues & fixes (referenced).&#x20;

1. **Input parsing can crash on empty or malformed input.**

   * You call `request.upper().split()` and then `split_request[0]` — empty input will raise `IndexError`. Also `ACCESS` handler uses `split_request[2]` without checking length.
     **Fix:** always check that `split_request` is non-empty and validate expected number of arguments before indexing. Return friendly error if not.

2. **Upper-casing entire input loses case-sensitive IDs/content.**

   * `request.upper()` will upper-case file IDs/paths that might be case-sensitive or content strings. Use a parser that only uppercases the command token (first word) and leaves the rest intact.
     **Fix:** parse into `cmd = words[0].upper()` then use `args = words[1:]` (not uppercased).

3. **Using `id` as a variable hides built-in `id()` and is confusing.**

   * Minor, but rename to `user_id` or `uid` to be explicit.

4. **Credentials sent in plain form to server.**

   * `send(server, f"AUTH {id} {password}")` transmits raw password text. That’s a serious security issue (see security section).&#x20;

5. **QS handling is brittle.**

   * `QS = True if len(sys.argv) == 3 else False` — that’s OK, but document how to run the quickstart. Also validate `sys.argv` indices before use.

6. **Help text and UX.**

   * Help printed from client is minimal — expand command usage and show required args. Also consider a safe `exit` alias.

---

## `server.py` — issues & fixes (referenced).&#x20;

1. **No socket options for reuse / graceful shutdown.**

   * `server.bind(ADDR)` is okay but set `SO_REUSEADDR` so you can restart quickly during development. On KeyboardInterrupt you `return` but you should close current connections and shutdown listening socket gracefully.
     **Fix:** use `server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` and ensure `server.close()` is called on exit.

2. **Thread accounting is simplistic.**

   * You pass `active_count()-1` as a thread id; that’s fine for debug prints but not a reliable identifier. Don’t rely on it for state.
     **Fix:** let the handler allocate a session id or use `uuid4()` if you need a unique ID.

3. **No per-connection try/except wrapper in the accept loop.**

   * If `handle_usr` raises in a thread, the thread dies but the server keeps listening — that’s okay, but add logging and ensure exceptions inside `handle_usr` are caught so resources are closed.

4. **No limit on connections or timeouts.**

   * Think about connection timeouts, max threads, and rejecting new connections gracefully.

---

## `deepwell_plan.sql` — schema issues & fixes (referenced).&#x20;

1. **FK column mismatches / typos**

   * Example: `mtfs` defines `leader_id` but the foreign key says `FOREIGN KEY(leader) REFERENCES users(id)` — should be `FOREIGN KEY(leader_id)`. Several index creation lines point at non-existing tables/columns (e.g., `containment_class` vs `containment_classes`).
     **Fix:** correct FK and index names to match the table/column names exactly.

2. **`scps` references `archived` index but `archived` column is absent.**

   * Add `archived BOOLEAN DEFAULT 0` to `scps` if needed or remove that index line.

3. **Missing `created_at` / `updated_at` fields for auditability.**

   * Add `created_at DATETIME DEFAULT CURRENT_TIMESTAMP` and `updated_at DATETIME` and ensure you update `updated_at` on modifications.

4. **Passwords in plain text**

   * You already annotated that in SQL comments — good. You must store hashed passwords (bcrypt/argon2) and never send raw passwords over socket.&#x20;

5. **Indexes & naming consistency**

   * Fix `idx_mtfs_leader ON mtfs(leader)` → `idx_mtfs_leader_id ON mtfs(leader_id)` and update other helper index names to match tables.

---

# Critical security and robustness items (must-do)

These are blockers before you consider distribution or demoing.

1. **Never send raw credentials on the wire.**

   * Change authentication flow to: (a) send credentials over TLS OR (b) use challenge-response and then issue a server-side session token (one-time token) for subsequent requests. If TLS is too much, at minimum use hashed PW comparison server-side and issue ephemeral session tokens (not raw password on every command). (Client currently sends raw `AUTH id password`.)&#x20;

2. **Server must enforce all security/clearance checks.**

   * Every request handler must validate session token and ensure the user has permissions for requested action (read/create/list). Never do checks only client-side.

3. **Path traversal protection.**

   * Do NOT accept arbitrary paths from clients. Map numeric IDs (scp id, site id) to server-owned filesystem paths. Client should request `FETCH SCP 123` where `123` is an ID; server resolves `deepwell/scps/123/desc.md`. Reject and log any string suggesting `../` etc.

4. **Atomic file writes + DB transactions.**

   * On `CREATE` or `UPDATE`, write to a temporary file, fsync, then move into place; update DB inside a transaction so you never end up with partial state. Use simple locking on write operations to avoid races.

5. **Audit everything important.**

   * Log login attempts, successful/failed accesses, create/delete operations in `audit_log` table. Use this for debugging and grading.

6. **Input validation**

   * Both client and server must validate argument counts and types (IDs numeric? length limits?). Make errors informative.

---

# Recommended API / protocol (no code — spec only)

Make the server expose a tiny, well-documented RPC set (string or JSON messages). Minimal set:

* `AUTH <id> <password>` → on success returns `{ok: true, session_token: "<token>", user_meta: {...}}` (but do not return raw password). Client stores token.
* `PING` → keep-alive / health check.
* `FETCH_FILE <session_token> <file_type> <id> [offset] [length]` → returns content chunk and metadata. (Server maps `file_type,id` -> path.)
* `LIST <session_token> <file_type> [filters]` → returns list of items with metadata (ids, titles, classification).
* `CREATE <session_token> <file_type> <metadata>` → create content; server returns new `id`.
* `SEARCH <session_token> <query>` → later, uses FTS index; returns matched ids & snippets.
* `LOGOUT <session_token>` → invalidates token.

Make request & response fully structured (JSON) if possible — avoids fragile space-parsing and makes future extension easy. If you continue with space-delimited strings, define exact grammar and escaping rules for spaces.

---

# Structural / repo refactor (recommended)

To keep things comprehensible and testable, I strongly recommend reorganizing code into a small package:

```
CS50xFP/
  server.py        # tiny bootstrap
  client.py        # tiny bootstrap
  scipnet/
    server/
      app.py        # Server class (listener + thread manager)
      handlers.py   # maps commands -> handler functions
      auth.py       # auth & sessions logic
      storage.py    # filesystem + db access (atomic ops)
      audit.py
    client/
      protocol.py   # sending/receiving + session management
      ui.py         # parsing and CLI helpers
    db/
      schema.sql
  deepwell/
    scps/
    sites/
    mtfs/
    SCiPNET.db
```

Why: makes unit testing, code ownership, and incremental refactor much easier. Move heavy `utils.*` logic into `scipnet.server.*` and `scipnet.client.*`.

---

# Prioritised checklist you can act on right away

(Implement in order — each item is small and concrete.)

1. **Immediate code hygiene (client / server).**

   * In `client.py`: stop uppercasing whole input, check `split_request` lengths, rename `id` var, and guard `ACCESS` arg indexes.&#x20;
   * In `server.py`: set `SO_REUSEADDR` and ensure `server.close()` on KeyboardInterrupt; log accept exceptions.&#x20;

2. **Define & document protocol.**

   * Create a one-page spec that lists allowed commands, required params, expected JSON responses, and error codes (e.g., PERMISSION\_DENIED, FILE\_NOT\_FOUND, INVALID\_TOKEN).

3. **Auth flow change.**

   * Stop sending raw password for every action. On login, the server validates and returns a `session_token` the client must use for subsequent actions.

4. **Server-side mapping of IDs -> paths.**

   * Ensure the server maps numeric IDs to filesystem paths; reject path strings from client.

5. **Atomic writes + DB transactions.**

   * Implement temp file + atomic move for creates/updates, and wrap DB updates in transactions.

6. **Schema fixes.**

   * Fix FK and index typos in `deepwell_plan.sql`, add `created_at`/`updated_at`, add `archived` boolean if you need it.&#x20;

7. **Audit logging.**

   * Insert audit log entries for logins, fetches, creates, failed attempts.

8. **Add tests for storage and auth.**

   * Add small unit tests using a temporary deepwell directory + ephemeral SQLite DB.

9. **Prepare for FTS search.**

   * When metadata is stable, add an FTS5 index on desc/cp files and expose `SEARCH`.

---

# Edge-cases to cover (dev checklist)

* Empty input or unknown commands (client validation).&#x20;
* Concurrent `CREATE` to same resource — ensure unique IDs.
* Client disconnect mid-write — server must clean up temp files.
* Corrupt or missing file referenced by DB — server should return `ORPHANED` or similar.

---

# Small style & naming housekeeping

* Use lower-case consistent DB filename (e.g., `scipnet.db`) to avoid case-sensitivity issues on different OSes.&#x20;
* Spell-check and fix table names & index names to avoid runtime SQL errors.&#x20;