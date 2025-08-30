架构设计
========

.. contents:: 本页内容
   :local:
   :depth: 2

概述
----

ModbusLink 采用**现代分层架构**设计，严格遵循**单一职责原则**和**开闭原则**，确保代码的可维护性、可扩展性和可测试性。

整体架构图
----------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                      应用层 (Application Layer)              │
   │                   用户代码和业务逻辑                         │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                      客户端层 (Client Layer)                │
   │         ModbusClient, AsyncModbusClient                     │
   │    • 高级API封装  • 数据类型转换  • 错误处理                │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                     协议层 (Protocol Layer)                 │
   │                    Modbus协议实现                           │
   │    • PDU构造  • 功能码处理  • 数据验证                      │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                     传输层 (Transport Layer)                │
   │         TCP, RTU, ASCII传输实现                             │
   │    • 连接管理  • 数据帧处理  • 校验计算                      │
   └─────────────────────────────────────────────────────────────┘
                                    │
   ┌─────────────────────────────────────────────────────────────┐
   │                      物理层 (Physical Layer)                │
   │                  以太网 / 串口 / 其他                       │
   └─────────────────────────────────────────────────────────────┘

核心设计原则
------------

1. **分层架构** (Layered Architecture)
   - 每层只与相邻层交互
   - 上层依赖于下层，下层不依赖上层
   - 便于独立测试和替换

2. **依赖注入** (Dependency Injection)
   - 客户端通过构造函数接收传输层实例
   - 降低耦合度，提高可测试性

3. **面向接口编程** (Interface-Oriented Programming)
   - 使用抽象基类定义接口
   - 具体实现可插拔替换

4. **策略模式** (Strategy Pattern)
   - 不同传输方式作为不同策略
   - 运行时切换传输策略

传输层设计
----------

传输层架构
~~~~~~~~~~

.. code-block:: text

   BaseTransport (ABC)
   ├── TcpTransport
   ├── RtuTransport  
   └── AsciiTransport

   AsyncBaseTransport (ABC)
   ├── AsyncTcpTransport
   ├── AsyncRtuTransport
   └── AsyncAsciiTransport

核心接口
~~~~~~~~

**同步传输接口**

.. code-block:: python

   class BaseTransport(ABC):
       @abstractmethod
       def connect(self) -> None:
           """建立连接"""
           
       @abstractmethod  
       def disconnect(self) -> None:
           """断开连接"""
           
       @abstractmethod
       def send_and_receive(self, data: bytes) -> bytes:
           """发送数据并接收响应"""

**异步传输接口**

.. code-block:: python

   class AsyncBaseTransport(ABC):
       @abstractmethod
       async def connect(self) -> None:
           """异步建立连接"""
           
       @abstractmethod
       async def disconnect(self) -> None:
           """异步断开连接"""
           
       @abstractmethod  
       async def send_and_receive(self, data: bytes) -> bytes:
           """异步发送数据并接收响应"""

传输实现细节
~~~~~~~~~~~~

**TCP传输 (Modbus TCP)**

.. code-block:: text

   MBAP Header (7 bytes) + PDU
   ┌──────┬──────┬──────┬──────┬──────────┬─────────────┐
   │ TID  │ PID  │ Length     │ Unit ID  │ Function    │
   │ (2)  │ (2)  │ (2)        │ (1)      │ Code + Data │
   └──────┴──────┴──────┴──────┴──────────┴─────────────┘

- **TID**: 事务标识符，用于匹配请求响应
- **PID**: 协议标识符，Modbus为0
- **Length**: 后续字节长度
- **Unit ID**: 单元标识符（从站地址）

**RTU传输 (Modbus RTU)**

.. code-block:: text

   RTU Frame
   ┌─────────┬─────────────┬─────────────┐
   │ Address │ Function    │ CRC-16      │
   │ (1)     │ Code + Data │ (2)         │
   └─────────┴─────────────┴─────────────┘

- **Address**: 从站地址 (1-247)
- **CRC-16**: 循环冗余校验，使用Modbus多项式
- **帧间隔**: 至少3.5个字符时间

**ASCII传输 (Modbus ASCII)**

.. code-block:: text

   ASCII Frame
   ┌───┬─────────┬─────────────┬─────┬─────┬───┐
   │ : │ Address │ Function    │ LRC │ CR  │ LF│
   │   │ (2)     │ Code + Data │ (2) │     │   │
   └───┴─────────┴─────────────┴─────┴─────┴───┘

- **Start**: 冒号字符 ':'
- **LRC**: 纵向冗余校验
- **End**: 回车换行 (CR LF)

客户端层设计
------------

客户端架构
~~~~~~~~~~

.. code-block:: text

   ┌─────────────────────────────────────┐
   │         高级数据类型API              │
   │  read_float32, write_string, etc.   │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         标准Modbus API               │
   │  read_holding_registers, etc.       │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         协议处理层                   │
   │  PDU构造, 响应解析, 异常处理         │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │         传输层接口                   │
   │  BaseTransport/AsyncBaseTransport   │
   └─────────────────────────────────────┘

设计模式应用
~~~~~~~~~~~~

**模板方法模式**

.. code-block:: python

   class ModbusClient:
       def _execute_request(self, slave_id: int, function_code: int, 
                          data: bytes) -> bytes:
           """模板方法：定义请求执行流程"""
           # 1. 构造PDU
           pdu = self._build_pdu(function_code, data)
           
           # 2. 发送并接收
           response = self._transport.send_and_receive(pdu)
           
           # 3. 验证响应
           self._validate_response(response, function_code)
           
           # 4. 解析数据
           return self._parse_response(response)

**装饰器模式**

.. code-block:: python

   def connection_required(func):
       """确保连接存在的装饰器"""
       def wrapper(self, *args, **kwargs):
           if not self._transport.is_connected():
               raise ConnectionError("Not connected")
           return func(self, *args, **kwargs)
       return wrapper

服务器层设计
------------

服务器架构
~~~~~~~~~~

.. code-block:: text

   ┌─────────────────────────────────────┐
   │        协议处理器                    │
   │   请求解析、响应构造、异常处理        │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │        数据存储层                    │
   │   线圈、寄存器的读写操作             │
   └─────────────────────────────────────┘
                     │
   ┌─────────────────────────────────────┐
   │        传输服务器                    │
   │   TCP/RTU/ASCII服务器实现           │
   └─────────────────────────────────────┘

数据存储设计
~~~~~~~~~~~~

.. code-block:: python

   class ModbusDataStore:
       """线程安全的Modbus数据存储"""
       
       def __init__(self, coils_size: int = 65536,
                    discrete_inputs_size: int = 65536,
                    holding_registers_size: int = 65536,
                    input_registers_size: int = 65536):
           self._coils = [False] * coils_size
           self._discrete_inputs = [False] * discrete_inputs_size  
           self._holding_registers = [0] * holding_registers_size
           self._input_registers = [0] * input_registers_size
           self._lock = threading.RLock()  # 可重入锁

工具层设计
----------

工具组件
~~~~~~~~

1. **CRC计算器**
   - 实现Modbus标准CRC-16算法
   - 支持表查找优化

2. **数据编码器**
   - 大小端字节序转换
   - 各种数据类型编解码

3. **日志系统**
   - 协议级调试信息
   - 可配置日志级别

错误处理架构
------------

异常层次结构
~~~~~~~~~~~~

.. code-block:: text

   ModbusLinkError (基础异常)
   ├── ConnectionError (连接相关)
   │   ├── ConnectionTimeoutError
   │   └── ConnectionRefusedError
   ├── ProtocolError (协议相关)
   │   ├── CRCError
   │   ├── InvalidResponseError
   │   └── FunctionCodeError
   └── DataError (数据相关)
       ├── AddressError
       └── ValueRangeError

异常处理策略
~~~~~~~~~~~~

1. **传输层异常**: 网络、串口通信错误
2. **协议层异常**: Modbus协议格式错误
3. **应用层异常**: 业务逻辑错误

性能优化设计
------------

连接池
~~~~~~

.. code-block:: python

   class ModbusConnectionPool:
       """Modbus连接池，支持连接复用"""
       
       def __init__(self, max_connections: int = 10):
           self._pool = asyncio.Queue(maxsize=max_connections)
           self._connections = set()
           
       async def acquire(self) -> AsyncModbusClient:
           """获取连接"""
           
       async def release(self, client: AsyncModbusClient):
           """释放连接"""

批量操作优化
~~~~~~~~~~~~

.. code-block:: python

   async def batch_read_registers(self, requests: List[ReadRequest]) -> List[List[int]]:
       """批量读取寄存器，自动优化为最少请求数"""
       # 合并连续地址的请求
       optimized_requests = self._optimize_requests(requests)
       
       # 并发执行
       tasks = [self._read_registers(**req) for req in optimized_requests]
       return await asyncio.gather(*tasks)

扩展性设计
----------

插件架构
~~~~~~~~

.. code-block:: python

   class ModbusPlugin(ABC):
       """Modbus插件基类"""
       
       @abstractmethod
       def on_request(self, request: ModbusRequest) -> ModbusRequest:
           """请求预处理"""
           
       @abstractmethod  
       def on_response(self, response: ModbusResponse) -> ModbusResponse:
           """响应后处理"""

自定义传输层
~~~~~~~~~~~~

.. code-block:: python

   class WebSocketTransport(AsyncBaseTransport):
       """WebSocket传输层示例"""
       
       async def connect(self):
           self._websocket = await websockets.connect(self._uri)
           
       async def send_and_receive(self, data: bytes) -> bytes:
           await self._websocket.send(data)
           response = await self._websocket.recv()
           return response

总结
----

ModbusLink的架构设计具有以下优势：

1. **清晰的分层结构**，每层职责明确
2. **高度的可扩展性**，支持自定义传输层和协议扩展
3. **优秀的性能表现**，支持异步和连接池
4. **完善的错误处理**，提供详细的异常信息
5. **良好的可测试性**，每层都可以独立测试

这种设计确保了ModbusLink既能满足当前需求，又具备未来扩展的灵活性。