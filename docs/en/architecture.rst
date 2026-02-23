Architecture Design
===================

1. verview
----------

ModbusLink adopts a **modern layered architecture** design, strictly following the **Single Responsibility Principle** and **Open/Closed Principle** to ensure code maintainability, extensibility, and testability.

2. Overall Architecture Diagram
-------------------------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                      Application Layer                      │
   │                 User Code and Business Logic                │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                      Client Layer                          │
   │         ModbusClient, AsyncModbusClient                    │
   │    • High-level API encapsulation  • Data type conversion  │
   │    • Error handling                                       │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                     Protocol Layer                         │
   │                   Modbus Protocol Implementation           │
   │    • PDU construction  • Function code handling           │
   │    • Data validation                                      │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                     Transport Layer                        │
   │         TCP, RTU, ASCII Transport Implementation          │
   │    • Connection management  • Data frame handling         │
   │    • Checksum calculation                                 │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                     Physical Layer                         │
   │                  Ethernet / Serial / Other                │
   └─────────────────────────────────────────────────────────────┘

3. Core Design Principles
-------------------------

1. **Layered Architecture**
   - Each layer only interacts with adjacent layers
   - Upper layers depend on lower layers, not vice versa
   - Facilitates independent testing and replacement

2. **Dependency Injection**
   - Clients receive transport layer instances through constructors
   - Reduces coupling, improves testability

3. **Interface-Oriented Programming**
   - Uses abstract base classes to define interfaces
   - Concrete implementations are pluggable

4. **Strategy Pattern**
   - Different transport methods as different strategies
   - Runtime transport strategy switching

5. Transport Layer Design
-------------------------

5.1 Transport Architecture
~~~~~~~~~~----------------------

.. code-block:: text

   SyncBaseTransport (ABC)
   ├── SyncTcpTransport
   ├── SyncRtuTransport
   └── SyncAsciiTransport

   AsyncBaseTransport (ABC)
   ├── AsyncTcpTransport
   ├── AsyncRtuTransport
   └── AsyncAsciiTransport

5.2 Core Interfaces
~~~~~~~~~~~~~~~~~~~

**Synchronous Transport Interface**

.. code-block:: python

   class SyncBaseTransport(ABC):
       @abstractmethod
       def open(self) -> None:
           """Open transport connection"""
           
       @abstractmethod  
       def close(self) -> None:
           """Close transport connection"""
           
       @abstractmethod
       def is_open(self) -> bool:
           """Check connection status"""

       @abstractmethod
       def flush(self) -> int:
           """Synchronously flush all pending data in receive buffer"""

       @abstractmethod
       def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
           """Send PDU and receive response"""

**Asynchronous Transport Interface**

.. code-block:: python

   class AsyncBaseTransport(ABC):
       @abstractmethod
       async def open(self) -> None:
           """Asynchronously open transport connection"""

       @abstractmethod
       async def close(self) -> None:
           """Asynchronously close transport connection"""

       @abstractmethod
       def is_open(self) -> bool:
           """Check connection status"""

       @abstractmethod
       async def flush(self) -> int:
           """Asynchronously flush all pending data in receive buffer"""

       @abstractmethod
       async def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
           """Asynchronously send PDU and receive response"""

5.3 Transport Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**TCP Transport (Modbus TCP)**

.. code-block:: text

   MBAP Header (7 bytes) + PDU
   ┌──────┬──────┬──────┬──────┬──────────┬─────────────┐
   │ TID  │ PID  │ Length     │ Unit ID  │ Function    │
   │ (2)  │ (2)  │ (2)        │ (1)      │ Code + Data │
   └──────┴──────┴──────┴──────┴──────────┴─────────────┘

- **TID**: Transaction Identifier for request-response matching
- **PID**: Protocol Identifier, 0 for Modbus
- **Length**: Length of following bytes
- **Unit ID**: Unit identifier (slave address)

**RTU Transport (Modbus RTU)**

.. code-block:: text

   RTU Frame
   ┌─────────┬─────────────┬─────────────┐
   │ Address │ Function    │ CRC-16      │
   │ (1)     │ Code + Data │ (2)         │
   └─────────┴─────────────┴─────────────┘

- **Address**: Slave address (1-247)
- **CRC-16**: Cyclic redundancy check using Modbus polynomial
- **Frame interval**: At least 3.5 character times

**ASCII Transport (Modbus ASCII)**

.. code-block:: text

   ASCII Frame
   ┌───┬─────────┬─────────────┬─────┬─────┬───┐
   │ : │ Address │ Function    │ LRC │ CR  │ LF│
   │   │ (2)     │ Code + Data │ (2) │     │   │
   └───┴─────────┴─────────────┴─────┴─────┴───┘

- **Start**: Colon character ':'
- **LRC**: Longitudinal redundancy check
- **End**: Carriage return and line feed (CR LF)

6. Client Layer Design
----------------------

6.1 Client Architecture
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ┌─────────────────────────────────────┐
   │         High-level Data Type API     │
   │  read_float32, write_string, etc.   │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         Standard Modbus API          │
   │  read_holding_registers, etc.       │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         Protocol Processing Layer    │
   │  PDU construction, response parsing, exception handling │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         Transport Layer Interface    │
   │  BaseTransport/AsyncBaseTransport   │
   └─────────────────────────────────────┘

6.2 Design Patterns Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template Method Pattern**

.. code-block:: python

   class SyncModbusClient:
       def _execute_request(self, slave_id: int, function_code: int, 
                          data: bytes) -> bytes:
           """Template method: defines request execution flow"""
           # 1. Construct PDU
           pdu = self._build_pdu(function_code, data)
           
           # 2. Send and receive
           response = self._transport.send_and_receive(pdu)
           
           # 3. Validate response
           self._validate_response(response, function_code)
           
           # 4. Parse data
           return self._parse_response(response)

**Decorator Pattern**

.. code-block:: python

   def connection_required(func):
       """Decorator to ensure connection exists"""
       def wrapper(self, *args, **kwargs):
           if not self._transport.is_connected():
               raise ConnectionError("Not connected")
           return func(self, *args, **kwargs)
       return wrapper

7. Server Layer Design
-------------------

7.1 Server Architecture
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ┌─────────────────────────────────────┐
   │        Protocol Handler             │
   │   Request parsing, response construction, exception handling │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │        Data Storage Layer           │
   │   Coil and register read/write operations │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │        Transport Server             │
   │   TCP/RTU/ASCII server implementation │
   └─────────────────────────────────────┘

7.2 Data Storage Design
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class ModbusDataStore:
       """Thread-safe Modbus data storage"""
       
       def __init__(self, coils_size: int = 65536,
                    discrete_inputs_size: int = 65536,
                    holding_registers_size: int = 65536,
                    input_registers_size: int = 65536):
           self._coils = [False] * coils_size
           self._discrete_inputs = [False] * discrete_inputs_size  
           self._holding_registers = [0] * holding_registers_size
           self._input_registers = [0] * input_registers_size
           self._lock = threading.RLock()  # Reentrant lock

8. Utility Layer Design
--------------------

8.1 Utility Components
~~~~~~~~~~~~~~~~~

1. **CRC Calculator**
   - Implements ModbusRTU standard CRC-16 algorithm
   - Supports lookup table optimization

1. **LRC Calculator**
   - Implements ModbusASCII standard LRC algorithm
   - Support verification data

3. **Data Encoder**
   - Big/little endian byte order conversion
   - Various data type encoding/decoding

9. Error Handling Architecture
---------------------------

9.1 Exception Hierarchy
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

ModbusLinkError (Base exception class)
├── CommunicationError (Base class for communication errors)
│   ├── ConnectError (Connection error exception)
│   └── TimeOutError (Timeout error exception)
├── ValidationError (Base class for data validation errors)
│   ├── CrcError (CRC validation error exception)
│   ├── LrcError (LRC validation error exception)
│   └── InvalidReplyError (Invalid reply error exception)
└── ModbusException (Protocol error)

9.2 Exception Handling Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Transport Layer Exceptions**: Network, serial communication errors
2. **Protocol Layer Exceptions**: Modbus protocol format errors
3. **Application Layer Exceptions**: Business logic errors

10. Performance Optimization Design
-------------------------------

10.1 Connection Pool
~~~~~~~~~~~~~~

.. code-block:: python

   class ModbusConnectionPool:
       """Modbus connection pool supporting connection reuse"""
       
       def __init__(self, max_connections: int = 10):
           self._pool = asyncio.Queue(maxsize=max_connections)
           self._connections = set()
           
       async def acquire(self) -> AsyncModbusClient:
           """Acquire connection"""
           
       async def release(self, client: AsyncModbusClient):
           """Release connection"""

10.2 Batch Operation Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def batch_read_registers(self, requests: List[ReadRequest]) -> List[List[int]]:
       """Batch read registers, automatically optimized to minimize requests"""
       # Merge consecutive address requests
       optimized_requests = self._optimize_requests(requests)
       
       # Concurrent execution
       tasks = [self._read_registers(**req) for req in optimized_requests]
       return await asyncio.gather(*tasks)

11. Extensibility Design
--------------------

11.1 Plugin Architecture
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class ModbusPlugin(ABC):
       """Modbus plugin base class"""
       
       @abstractmethod
       def on_request(self, request: SyncModbusRequest) -> SyncModbusRequest:
           """Request preprocessing"""
           
       @abstractmethod  
       def on_response(self, response: SyncModbusResponse) -> SyncModbusResponse:
           """Response postprocessing"""

11.2 Custom Transport Layer
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class WebSocketTransport(AsyncBaseTransport):
       """WebSocket transport layer example"""
       
       async def connect(self):
           self._websocket = await websockets.connect(self._uri)
           
       async def send_and_receive(self, data: bytes) -> bytes:
           await self._websocket.send(data)
           response = await self._websocket.recv()
           return response

12. Summary
-------

ModbusLink's architecture design offers the following advantages:

1. **Clear layered structure** with well-defined responsibilities for each layer
2. **High extensibility** supporting custom transport layers and protocol extensions
3. **Excellent performance** with async support and connection pooling
4. **Comprehensive error handling** providing detailed exception information
5. **Good testability** with each layer independently testable

This design ensures ModbusLink can meet current requirements while providing flexibility for future extensions.