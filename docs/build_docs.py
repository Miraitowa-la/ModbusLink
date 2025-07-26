#!/usr/bin/env python3
"""
Local documentation build script for ModbusLink.

This script builds both English and Chinese versions of the documentation
and creates a unified index page for easy navigation.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def create_index_page(build_dir):
    """Create the main index page with language selection."""
    index_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModbusLink Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
        }
        .language-selector {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 2rem;
        }
        .language-card {
            background: #3498db;
            color: white;
            padding: 2rem;
            border-radius: 8px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        .language-card:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        .language-card h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }
        .language-card p {
            margin: 0;
            opacity: 0.9;
        }
        .description {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .build-info {
            text-align: center;
            color: #95a5a6;
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #ecf0f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ModbusLink Documentation</h1>
        <p class="description">
            Welcome to ModbusLink documentation. Choose your preferred language to get started.
            <br>
            欢迎使用ModbusLink文档。请选择您的首选语言开始使用。
        </p>
        <div class="language-selector">
            <a href="en/index.html" class="language-card">
                <h2>English</h2>
                <p>English Documentation</p>
            </a>
            <a href="zh/index.html" class="language-card">
                <h2>中文</h2>
                <p>中文文档</p>
            </a>
        </div>
        <div class="build-info">
            Built with Sphinx • ModbusLink Documentation
        </div>
    </div>
</body>
</html>
'''
    
    index_path = build_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"Created index page: {index_path}")


def main():
    """Main build function."""
    # Get the docs directory
    docs_dir = Path(__file__).parent
    build_dir = docs_dir / '_build' / 'html'
    
    print("Building ModbusLink Documentation")
    print("=" * 40)
    
    # Clean build directory
    if build_dir.exists():
        print("Cleaning build directory...")
        shutil.rmtree(build_dir)
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Build English documentation
    print("\nBuilding English documentation...")
    en_build_dir = build_dir / 'en'
    run_command([
        'sphinx-build',
        '-b', 'html',
        '-c', str(docs_dir / 'en'),
        str(docs_dir / 'en'),
        str(en_build_dir)
    ])
    
    # Build Chinese documentation
    print("\nBuilding Chinese documentation...")
    zh_build_dir = build_dir / 'zh'
    run_command([
        'sphinx-build',
        '-b', 'html',
        '-c', str(docs_dir / 'zh'),
        str(docs_dir / 'zh'),
        str(zh_build_dir)
    ])
    
    # Create main index page
    print("\nCreating main index page...")
    create_index_page(build_dir)
    
    print("\n" + "=" * 40)
    print("Documentation build completed!")
    print(f"Output directory: {build_dir}")
    print(f"Open {build_dir / 'index.html'} in your browser to view the documentation.")


if __name__ == '__main__':
    main()