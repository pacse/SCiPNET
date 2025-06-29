# looking at how we would do text processing with perl.
# this is my first Perl script, so pardon bad form.
# make script executable: chmod +x scps.pl

#!/usr/bin/perl
use strict;
use warnings;

# set encoding to UTF-8
use open ":std", ":encoding(UTF-8)";

# Slurp input from python
undef $/;
my $html = <STDIN>;

# === modify html ===
# proper italics
$html =~ s{<em>}{*}gis; # replace all <em> with *, g: match all, i: case insensitive, s: contd with \n ect
$html =~ s{</em>}{*}gis; # replace all </em> with *

# proper bolding
$html =~ s{<strong>}{**}gis; # replace all <strong> with **
$html =~ s{</strong>}{**}gis; # replace all </strong> with **

# remove blank <p> tags
$html =~ s{<p></p>}{}gis;

# === print html ===
print $html;