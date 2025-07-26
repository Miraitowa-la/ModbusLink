# ModbusLink Documentation

This directory contains the complete documentation system for ModbusLink, supporting both English and Chinese versions.

## 📁 Directory Structure

```
docs/
├── en/                     # English documentation source files
│   ├── index.rst          # English main page
│   ├── installation.rst   # Installation guide
│   ├── quickstart.rst     # Quick start guide
│   ├── user_guide.rst     # Comprehensive user guide
│   ├── api_reference.rst  # API documentation
│   └── examples.rst       # Code examples
├── zh/                     # Chinese documentation source files
│   ├── index.rst          # Chinese main page
│   ├── installation.rst   # 安装指南
│   ├── quickstart.rst     # 快速开始
│   ├── user_guide.rst     # 用户指南
│   ├── api_reference.rst  # API参考
│   └── examples.rst       # 示例代码
├── conf.py                 # Main Sphinx configuration
├── conf_zh.py             # Chinese-specific configuration
├── requirements.txt       # Documentation dependencies
├── Makefile               # Unix/Linux build commands
├── build_docs.py          # Python build script
├── build_docs.ps1         # PowerShell build script
└── _build/                 # Generated documentation (created after build)
    └── html/
        ├── index.html      # Main language selection page
        ├── en/             # English documentation
        └── zh/             # Chinese documentation
```

## 🚀 Quick Start

### Prerequisites

Install the required dependencies:

```bash
pip install -r docs/requirements.txt
```

### Building Documentation

#### Option 1: Python Script (Recommended)

```bash
# From project root
python docs/build_docs.py
```

#### Option 2: PowerShell Script (Windows)

```powershell
# From project root
.\docs\build_docs.ps1
```

#### Option 3: Make (Unix/Linux/macOS)

```bash
# From docs directory
cd docs
make html-all  # Build both languages
make html-en   # Build English only
make html-zh   # Build Chinese only
```

#### Option 4: Manual Sphinx Commands

```bash
# English documentation
sphinx-build -b html -c docs -D language=en docs/en docs/_build/html/en

# Chinese documentation
sphinx-build -b html -c docs -D language=zh_CN docs/zh docs/_build/html/zh
```

### Viewing Documentation

After building, open `docs/_build/html/index.html` in your browser. This page provides:

- 🌐 **Language Selection**: Choose between English and Chinese
- 🎨 **Modern UI**: Clean, responsive design
- 📱 **Mobile Friendly**: Works on all devices

## 🔧 Configuration

### Main Configuration (`conf.py`)

- **Project Information**: Name, version, author
- **Sphinx Extensions**: autodoc, napoleon, sphinx-design, etc.
- **HTML Theme**: Read the Docs theme
- **Internationalization**: Language settings

### Chinese Configuration (`conf_zh.py`)

- **Language**: Set to `zh_CN`
- **Localized Settings**: Chinese-specific configurations

## 📚 Documentation Content

### English Documentation

1. **Installation**: System requirements, installation methods
2. **Quick Start**: Basic concepts, first steps
3. **User Guide**: Comprehensive feature coverage
4. **API Reference**: Complete class and method documentation
5. **Examples**: Real-world usage patterns

### Chinese Documentation (中文文档)

1. **安装指南**: 系统要求，安装方法
2. **快速开始**: 基本概念，入门步骤
3. **用户指南**: 全面的功能介绍
4. **API参考**: 完整的类和方法文档
5. **示例**: 实际使用模式

## 🚀 Deployment

### GitHub Pages

The documentation is automatically deployed via GitHub Actions (`.github/workflows/docs.yml`):

- **Trigger**: Push to main/master branch
- **Build**: Both English and Chinese versions
- **Deploy**: GitHub Pages with unified entry point

### Read the Docs

Configuration file: `.readthedocs.yaml`

- **Platform**: Ubuntu 22.04
- **Python**: 3.9
- **Formats**: HTML, PDF, ePub
- **Requirements**: Automatic installation

### Local Development Server

For live preview during development:

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live server for English docs
sphinx-autobuild -c docs docs/en docs/_build/html/en

# Start live server for Chinese docs
sphinx-autobuild -c docs -D language=zh_CN docs/zh docs/_build/html/zh
```

## 🎨 Customization

### Adding New Pages

1. Create `.rst` files in `docs/en/` and `docs/zh/`
2. Add entries to the `toctree` in respective `index.rst` files
3. Rebuild documentation

### Styling

- **Theme**: Modify `html_theme_options` in `conf.py`
- **CSS**: Add custom styles to `_static/custom.css` (create if needed)
- **Logo**: Set `html_logo` in configuration

### Extensions

Current extensions:
- `sphinx.ext.autodoc`: Automatic API documentation
- `sphinx.ext.napoleon`: Google/NumPy docstring support
- `sphinx_design`: Modern UI components
- `sphinx_rtd_theme`: Read the Docs theme

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r docs/requirements.txt
   ```

2. **Build Errors**
   - Check Sphinx configuration syntax
   - Verify all referenced files exist
   - Review error logs for specific issues

3. **Missing Static Files**
   - Ensure `_static` directory exists if referenced
   - Comment out `html_static_path` if not using custom static files

4. **Intersphinx Errors**
   - Verify external documentation URLs
   - Check network connectivity

### Debug Mode

For verbose output:

```bash
sphinx-build -v -b html -c docs docs/en docs/_build/html/en
```

## 📝 Contributing

When contributing to documentation:

1. **Content**: Update both English and Chinese versions
2. **Format**: Follow reStructuredText syntax
3. **Build**: Test locally before submitting
4. **Review**: Ensure all links and references work

## 📄 License

Documentation is licensed under the same terms as the ModbusLink project (MIT License).