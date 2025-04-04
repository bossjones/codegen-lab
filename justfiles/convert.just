# Remarshal and format conversion commands

# Set default remarshal command prefix
REMARSHAL_RUN := "uv run remarshal"

# Initialize remarshal installation
[group('convert')]
install-remarshal:
	uv tool install remarshal

# Show remarshal version
[group('convert')]
remarshal-version:
	{{REMARSHAL_RUN}} --version

# Basic format conversions

# Convert JSON to TOML
[group('convert')]
json2toml src dst:
	{{REMARSHAL_RUN}} --from json --to toml --input {{src}} --output {{dst}}

# Convert JSON to YAML
[group('convert')]
json2yaml src dst:
	{{REMARSHAL_RUN}} --from json --to yaml --input {{src}} --output {{dst}}

# Convert TOML to JSON
[group('convert')]
toml2json src dst:
	{{REMARSHAL_RUN}} --from toml --to json --input {{src}} --output {{dst}}

# Convert TOML to YAML
[group('convert')]
toml2yaml src dst:
	{{REMARSHAL_RUN}} --from toml --to yaml --input {{src}} --output {{dst}}

# Convert YAML to JSON
[group('convert')]
yaml2json src dst:
	{{REMARSHAL_RUN}} --from yaml --to json --input {{src}} --output {{dst}}

# Convert YAML to TOML
[group('convert')]
yaml2toml src dst:
	{{REMARSHAL_RUN}} --from yaml --to toml --input {{src}} --output {{dst}}

# Python code conversions

# Convert JSON to Python
[group('convert')]
json2py src dst:
	{{REMARSHAL_RUN}} --from json --to python --input {{src}} --output {{dst}}

# Convert TOML to Python
[group('convert')]
toml2py src dst:
	{{REMARSHAL_RUN}} --from toml --to python --input {{src}} --output {{dst}}

# Convert YAML to Python
[group('convert')]
yaml2py src dst:
	{{REMARSHAL_RUN}} --from yaml --to python --input {{src}} --output {{dst}}

# Advanced conversion options

# Convert with key sorting
[group('convert')]
convert-sorted src dst from to:
	{{REMARSHAL_RUN}} --from {{from}} --to {{to}} --input {{src}} --output {{dst}} --sort-keys

# Convert with stringification (for lossless conversion)
[group('convert')]
convert-stringify src dst from to:
	{{REMARSHAL_RUN}} --from {{from}} --to {{to}} --input {{src}} --output {{dst}} --stringify

# Convert with wrapping (for non-dictionary data)
[group('convert')]
convert-wrap src dst from to key:
	{{REMARSHAL_RUN}} --from {{from}} --to {{to}} --input {{src}} --output {{dst}} --wrap {{key}}

# Convert with unwrapping
[group('convert')]
convert-unwrap src dst from to key:
	{{REMARSHAL_RUN}} --from {{from}} --to {{to}} --input {{src}} --output {{dst}} --unwrap {{key}}
