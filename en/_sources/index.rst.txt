ModbusLink Documentation
========================

.. image:: https://static.pepy.tech/badge/modbuslink
   :target: https://pepy.tech/projects/modbuslink
   :alt: PyPI Downloads

.. image:: https://img.shields.io/pypi/v/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: Python Version

.. image:: https://img.shields.io/github/license/Miraitowa-la/ModbusLink
   :target: https://github.com/Miraitowa-la/ModbusLink/blob/main/LICENSE.txt
   :alt: License

Welcome to ModbusLink's documentation!

ModbusLink is a modern, high-performance Python Modbus library designed for industrial automation, IoT applications, and SCADA systems. Built with modern Python practices, it provides unparalleled ease of use while maintaining enterprise-grade reliability.

Documentation Sections
======================

Getting Started
---------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: ⚡ 30-Second Demo
      :link: quickstart
      :link-type: doc
      :class-card: quickstart-card

      Get up and running with ModbusLink in minutes. Learn the basics and see your first Modbus communication.

   .. grid-item-card:: 🛠️ Installation Guide
      :link: installation
      :link-type: doc
      :class-card: install-card

      Detailed installation guide including system requirements, dependencies, and environment setup.

Core Features
-------------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 📖 User Guide
      :link: user_guide
      :link-type: doc
      :class-card: guide-card

      Comprehensive guide covering all features, from basic operations to advanced configurations.

   .. grid-item-card:: 🏗️ Architecture Design
      :link: architecture
      :link-type: doc
      :class-card: arch-card

      Deep dive into ModbusLink's layered architecture and design principles.

   .. grid-item-card:: 📚 API Reference
      :link: api_reference
      :link-type: doc
      :class-card: api-card

      Complete API documentation with detailed class and method descriptions.

Real-World Applications
-----------------------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 💡 Code Examples
      :link: examples
      :link-type: doc
      :class-card: example-card

      Rich collection of real-world examples covering various industrial application scenarios.

   .. grid-item-card:: ⚡ Performance Tuning
      :link: performance
      :link-type: doc
      :class-card: perf-card

      Performance optimization techniques and concurrent processing best practices.

   .. grid-item-card:: 🔧 Troubleshooting
      :link: troubleshooting
      :link-type: doc
      :class-card: trouble-card

      Common issues solutions and debugging techniques.

Key Features
============

.. list-table:: ModbusLink Core Features
   :widths: 20 40 40
   :header-rows: 1

   * - Feature
     - Description
     - Benefit
   * - 🏗️ **Layered Architecture**
     - Clean separation of concerns
     - Easy maintenance & extension
   * - 🔌 **Universal Transports**
     - TCP, RTU, ASCII support
     - Works with any Modbus device
   * - ⚡ **Async Performance**
     - Native asyncio support
     - Handle 1000+ concurrent connections
   * - 🛠️ **Developer Experience**
     - Intuitive APIs & full typing
     - Faster development & fewer bugs
   * - 📊 **Rich Data Types**
     - float32, int32, strings & more
     - Handle complex industrial data
   * - 🔍 **Advanced Debugging**
     - Protocol-level monitoring
     - Rapid troubleshooting
   * - 🖥️ **Complete Server**
     - Full server implementation
     - Build custom Modbus devices
   * - 🎯 **Production Ready**
     - Comprehensive error handling
     - Deploy with confidence

Supported Modbus Function Codes
===============================

.. list-table::
   :widths: 15 25 60
   :header-rows: 1

   * - Function Code
     - Function Name
     - Description
   * - **0x01**
     - Read Coils
     - Read status of one or more coils (boolean values)
   * - **0x02**
     - Read Discrete Inputs
     - Read status of one or more discrete inputs (read-only boolean values)
   * - **0x03**
     - Read Holding Registers
     - Read values of one or more holding registers (16-bit integers)
   * - **0x04**
     - Read Input Registers
     - Read values of one or more input registers (read-only 16-bit integers)
   * - **0x05**
     - Write Single Coil
     - Write a single coil value to specified address
   * - **0x06**
     - Write Single Register
     - Write a single register value to specified address
   * - **0x0F**
     - Write Multiple Coils
     - Write multiple coil values to consecutive addresses
   * - **0x10**
     - Write Multiple Registers
     - Write multiple register values to consecutive addresses

Get Started Now
===============

🚀 Ready to dive in? Head to :doc:`installation` to install ModbusLink, then check out :doc:`quickstart` for a detailed tutorial!

Community and Support
=====================

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 📖 GitHub Project
      :link: https://github.com/Miraitowa-la/ModbusLink
      :link-type: url

      Source code, issue reports, and feature requests

   .. grid-item-card:: 📦 PyPI Package
      :link: https://pypi.org/project/modbuslink/
      :link-type: url

      Official releases and version history

Version Information
===================

ModbusLink 1.5.0
----------------

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   installation
   quickstart
   architecture

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   user_guide
   advanced_guide
   performance
   production

.. toctree::
   :maxdepth: 2
   :caption: Examples & Practices
   :hidden:

   examples
   best_practices
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Documentation
   :hidden:

   api_reference

.. toctree::
   :maxdepth: 1
   :caption: Others
   :hidden:

   changelog
   contributing