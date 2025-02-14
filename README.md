# fontinfo.py

A Python script for viewing and modifying OpenType font name tables.

## Dependencies

```
pip install fonttools
pip install wcwidth  # Optional, for better Unicode character width handling
```

## Usage

### View Font Information
```
python fontinfo.py "path/to/font.ttf"
```

### Modify Font Family Name
```
python fontinfo.py -f "New Family Name" "path/to/font.ttf"
```

### Replace String in Name Table
```
python fontinfo.py -d "old string" -n "new string" "path/to/font.ttf"
```

### Batch Process Multiple Fonts
```
python fontinfo.py -f "New Family Name" "font1.ttf" "font2.ttf" "font3.ttf"
```

### Show Help Message
```
python fontinfo.py -h
```

## Options

| Option | Description |
|--------|-------------|
| `-f`, `--family-name` | Set new font family name |
| `-d`, `--old-string` | Specify string to be replaced |
| `-n`, `--new-string` | Specify replacement string |
| `-w`, `--win` | Enable Windows-compatible style naming |

## Notes

- The script automatically handles both Windows and Mac platform-specific name entries
- Proper Unicode character display requires the optional wcwidth module
- Modifications are made in-place; consider backing up fonts before modification

## Acknowledgments

This script is a modification of the original fontname.py script created by Chris Simpkins (https://github.com/chrissimpkins/fontname.py).
