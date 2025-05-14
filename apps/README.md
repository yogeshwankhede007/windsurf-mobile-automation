# Mobile Applications

This directory contains the mobile application files (APK/IPA) used for testing.

## Directory Structure

```
apps/
├── android/         # Android APK files
│   └── README.md
├── ios/             # iOS IPA files
│   └── README.md
└── README.md        # This file
```

## Adding Applications

### Android
1. Place your `.apk` files in the `android/` directory
2. Update the `config.py` with the correct path to your APK file

### iOS
1. Place your `.ipa` files in the `ios/` directory
2. Update the `config.py` with the correct path to your IPA file

## Best Practices

- Use descriptive filenames that include version information
- Add a corresponding `.md` file with details about the app version
- Keep only the necessary versions to avoid repository bloat
- Update the `config.py` file when adding new versions
