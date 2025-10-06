# Developer Documentation Changelog

All notable changes to the developer documentation site will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial developer documentation site structure
- Complete navigation with 16 major sections
- Architecture documentation with system overview, module map, and data flow
- Overview section with introduction, audience, and compatibility guide
- README with contribution guidelines
- requirements.txt for building the site
- Site switcher between user docs and developer docs
- MkDocs configuration with Material theme

### Changed
- None yet

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

---

## [0.56.0-beta] - 2025-10-05

**Compatible with app version:** v0.56.x

### Added
- Developer documentation site launched on separate `docs/devs` branch
- Comprehensive architecture documentation
- API reference structure for all modules
- Codebase tour framework
- Configuration and data layer documentation
- UI/TUI architecture documentation
- Extensibility and plugin documentation
- Build, CI/CD, and release process documentation
- Quality assurance and testing documentation
- Performance optimization guides
- Security documentation
- Contributing guidelines
- Architecture Decision Records (ADRs) framework
- Known issues tracking
- Maintenance and docs health checklist
- Glossary and appendices

### Changed
- Documentation now published independently from user docs
- Separate GitHub Pages publishing workflow

---

## Version History

### Version Compatibility Matrix

| Dev Docs Version | App Version | Branch | Status |
|------------------|-------------|--------|--------|
| 0.56.0-beta | v0.56.x | `docs/devs` | ✅ Current |

---

## Release Process for Developer Docs

When updating developer docs:

1. **Make changes** on the `docs/devs` branch
2. **Update this CHANGELOG** with the changes
3. **Update version compatibility** if app version changed
4. **Build and test locally:**
   ```bash
   mkdocs serve -f mkdocs-dev.yml
   ```
5. **Commit and push** to `docs/devs` branch
6. **GitHub Actions** automatically builds and publishes

---

## Contributing

See [Contributing to Docs](overview/contributing-docs.md) for how to contribute to this changelog.

Every PR that changes developer docs should:

- ✅ Update this CHANGELOG in the "Unreleased" section
- ✅ Follow conventional commits format
- ✅ Update version compatibility if needed

---

## Changelog Conventions

### Categories

- **Added:** New documentation, new sections, new examples
- **Changed:** Updates to existing docs, reorganization
- **Deprecated:** Documentation for deprecated features (flagged for removal)
- **Removed:** Deleted sections or pages
- **Fixed:** Corrections, broken link fixes, typos
- **Security:** Security-related documentation updates

### Commit Message Format

```
docs: <type>: <description>

Examples:
docs: add API reference for services.publish
docs: fix broken links in architecture section
docs: update compatibility matrix for v0.56
```

---

## Links

- [Developer Docs Site](https://0xpix.github.io/Hei-DataHub/dev)
- [User Docs Site](https://0xpix.github.io/Hei-DataHub)
- [GitHub Repository](https://github.com/0xpix/Hei-DataHub)
