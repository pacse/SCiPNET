-- reviewed by ChatGPT, all edits marked in ()

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL, -- add later: store securely (hashing + salting)
    clearance_level_id INTEGER NOT NULL,
    title_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    override_phrase TEXT, -- Override phrase, optional field (phrase -> override_phrase for clarity)
    last_login DATETIME DEFAULT NULL,

    FOREIGN KEY(site_id) REFERENCES sites(id),
    FOREIGN KEY(clearance_level_id) REFERENCES clearance_levels(id),
    FOREIGN KEY(title_id) REFERENCES titles(id)
    )

CREATE TABLE scps (
    id INTEGER PRIMARY KEY NOT NULL,
    classification_level_id INTEGER NOT NULL,
    containment_class_id INTEGER NOT NULL,
    secondary_class_id INTEGER,
    disruption_class_id INTEGER,
    risk_class_id INTEGER,
    site_responsible_id INTEGER,
    assigned_task_force_id INTEGER,
    status TEXT DEFAULT "active" CHECK(status IN ("active", "neutralized", "explained", "deleted")) NOT NULL -- Thanks ChatGPT for improving this from a bool :)

    FOREIGN KEY(classification_level_id) REFERENCES clearance_levels(id),
    FOREIGN KEY(containment_class_id) REFERENCES containment_classes(id),
    FOREIGN KEY(secondary_class_id) REFERENCES secondary_classes(id),
    FOREIGN KEY(disruption_class_id) REFERENCES disruption_classes(id),
    FOREIGN KEY(risk_class_id) REFERENCES risk_classes(id),
    FOREIGN KEY(site_responsible_id) REFERENCES sites(id),
    FOREIGN KEY(assigned_task_force_id) REFERENCES mtfs(id)
    )

CREATE TABLE mtfs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- eg. Epsilon-6
    nickname TEXT NOT NULL, -- eg. "Village Idiots"
    leader_id INTEGER, -- probably null when ripped from wikidot
    assigned_site_id INTEGER,
    active BOOLEAN DEFAULT TRUE NOT NULL,

    FOREIGN KEY(leader_id) REFERENCES users(id),
    FOREIGN KEY(assigned_site_id) REFERENCES sites(id)
    )

CREATE TABLE sites (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    director INTEGER,
    FOREIGN KEY(director) REFERENCES users(id)
    )

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL, -- what happened (ie. login, file change, ect)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- optional additional details (eg. action description)

    FOREIGN KEY(user_id) REFERENCES users(id)
    )

-- helper tables
CREATE TABLE colours ( -- colours to use when printing markdown
    id INTEGER PRIMARY KEY
    hex_code INTEGER NOT NULL -- convert to and from hex
)

CREATE TABLE clearance_levels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- ie. Level 3 - Secret, Level 5 - Thaumiel, ect.
    )

CREATE TABLE containment_classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- eg. Safe, Euclid, Keter, ect.
    )

CREATE TABLE secondary_classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- eg. Thaumiel, Appolyion, ect.
    )

CREATE TABLE disruption_classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- eg. Dark, Vlam, ect.
    )

CREATE TABLE risk_classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- eg. Notice, Danger, ect.
    )

CREATE TABLE titles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL, -- title (eg. site director, junior researcher, O5 council member)
    )

/*
Deepwell folder structure:
deepwell
  ├─ SCiPNET.db
  ├─ descs
  │ ├─ clearance_levels
	│ │ ├─ 1.md # wikidot description of clearance level, matched with id
  │ │ ├─ 2.md
  │ │ ├─ ...
  │ ├─ containment_classes
	│ │ ├─ 1.md # same as clearance_levels
  │ │ ├─ ...
  │ ├─ disruption_classes
  │ │ ├─ ...
  │ ├─ risk_classes
  │ │ ├─ ...
  │ ├─ secondary_classes
  │ │ ├─ ...
  │ ├─ titles
  │ │ ├─ ...
	├─ scps
  │ ├─ 001
	│ │ ├─ cp.md # containment procedures with less chars
	│ │ ├─ desc.md # description
	│ │ ├─ addenda
	│ │ │ └─ 1.md # Addendum index (start at 1)
	│ │ ├─ hist_cps # past containment procedures, updates when file changes (if still same scp) for narrative
	│ │ │ └─ 1.md
	│ │ └─ hist_descs # past descriptions, updates when file changes (if still same scp) for narrative
	│ │   └─ 1.md
  │ └─ 002
  │   └─ # same structure as 001
	├─ sites
  │ ├─ # site name, from deepwell
	│ │ ├─ desc.md # site description
	│ │ ├─ loc.md # site location
	│ │ └─ security.md # site security details: Area monitoring (move to deepwell?)
	│ │ └─ dossier.md # site dossier, any others?
  │ └─ # other sites
	├─ mtfs
  │ ├─ 1 # mtf id from deepwell
	│ │ ├─ desc.md # mtf description
	│ │ └─ missions # all missions # classified, specified in filename
	│ │   └─ 5-1.md # {classification level}-{mission index (start at 1)}
  │ └─ # other mtfs
	└─ users # any files associated with users
    ├─ 1 # uid from deepwell
	  │ ├─ projs.md # user projects, eg assigned scps, roles there, ect
	  │ └─ standing.md # disciplinary history (out of clearance file access, ect)
    └─ # other users

└─ ├─ │

Indexes: All reccomended by ChatGPT. Tip:
ALways index foreign keys for joins
*/
-- user indexes
CREATE INDEX idx_users_name ON users(name)
CREATE INDEX idx_users_clearance_level_id ON users(clearance_level_id)
CREATE INDEX idx_users_site_id ON users(site_id)
CREATE INDEX idx_users_title_id ON  users(title_id)
-- scp indexes
CREATE INDEX idx_scps_classification_level_id ON scps(classification_level_id)
CREATE INDEX idx_scps_containment_class_id ON scps(containment_class_id)
CREATE INDEX idx_scps_site_responsible_id ON scps(site_responsible_id)
CREATE INDEX idx_scps_assigned_task_force_id ON scps(assigned_task_force_id)
CREATE INDEX idx_scps_archived ON scps(archived)
-- mtf index
CREATE INDEX idx_mtfs_leader ON mtfs(leader)
-- site index
CREATE INDEX idx_sites_director ON sites(director)
-- audit log indexes
CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp)
-- helper table indexes
CREATE INDEX idx_clearance_levels_name ON clearance_levels(name)
CREATE INDEX idx_containment_class_name ON containment_class(name)
CREATE INDEX idx_secondary_class_name ON secondary_class(name)
CREATE INDEX idx_disruption_class_name ON disruption_class(name)
CREATE INDEX idx_risk_class_name ON risk_class(name)
CREATE INDEX idx_titles_name ON titles(name)