# Orbit Browser

Orbit is a modern, privacy-focused web browser developed by SafeCircle. Designed for families, schools, and privacy-conscious users, Orbit delivers seamless and secure browsing with preinstalled security extensions and a distraction-free interface by default. Built on open-source technology, it offers transparency and trust for all users.

### Key Features

- **Privacy-first architecture**: Designed to avoid tracking and data collection by default.
- **Preinstalled security tools**: Bundled with powerful security/privacy extensions out-of-the-box.
- **Distraction-free interface**: Minimal UI with focus features for education and family contexts.
- **Open-source core**: Built transparently, enabling community trust and extensibility.

### Target Users

Orbit is ideal for:
- Families looking for digital protection for children and elders.
- Schools wanting secure and manageable browsers for students.
- Anyone seeking a private, safe browsing experience without ad-tech tracking.

### Getting Started

Orbit is a Firefox fork built with [Surfer](https://github.com/zen-browser/surfer). You need Node.js (see `.nvmrc`), Python (see `.python-version`) and Rust (see `.rust-toolchain`).

```bash
git clone https://github.com/safecircleia/orbit.git
cd orbit
npm install
npm run init     # download Firefox source, import Orbit's changes, bootstrap
npm run build    # build Orbit
npm start        # run it
```

Platform-specific build settings live in `configs/` (for example `configs/macos/mozconfig`).

### Development

- `npm run lint` / `npm run lint:fix`: ESLint and Prettier
- `npm test`: run the test suite
- `npm run export`: export your changes in `engine/` back into `src/`

Contributions are welcome. Please open an issue or pull request to report bugs or suggest improvements.

### Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

### License

Orbit is licensed under the [Mozilla Public License 2.0](LICENSE). Bundled third-party components keep their own licenses.

### Learn More

Downloads and releases: https://github.com/safecircleia/orbit/releases
