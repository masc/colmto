echo "# Radon\n"
echo "## Cyclomatic Complexity\n"
echo "| File | Type | R:C | Module | CC  |\n|:---- |:---- |:---:|:------ |:--- |"
radon cc --show-closures -x F --total-average -s colmto | sed \
-e 's/^    /||/g' \
-e '/^||/ s/ - /|/g' \
-e '/^||/ s/ /|/g' \
-e '/^||/ s/|(/ (/g' \
-e '/^||/ s/$/|/' \
-e '/^[a-zA-Z]/ s/^/|`/' \
-e '/^|`[a-zA-Z]/ s/$/`|||||/' \
-e '/^||/ s/|[[:alnum:]\.\_]\{2\}[[:alnum:]\.\_]*|/|`&`|/g' \
-e '/^||/ s/|`|/|`/' \
-e '/^||/ s/|`|/`|/' \
-e '/|`Average[[:print:]]*`|/ s/|//g'
echo "\n## Maintainability Index\n"
echo "| Module | MI  |\n|:------ |:--- |"
radon mi -x F -s colmto | sed \
-e 's/ - /`|/g' \
-e '/^[a-zA-Z]/ s/^/|`/' \
-e '/^|`[a-zA-Z]/ s/$/|/'
