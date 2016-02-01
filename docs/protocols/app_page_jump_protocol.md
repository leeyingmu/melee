### App页面跳转协议（Page Route Protocol）

为规范App各平台（H5、Android、iOS）页面间跳转过程，同时保留足够的跳转灵活性，特指定该跳转协议。

#### 1. 协议目标

- a. 支持`Native`页面间跳转，支持`Native`页面跳转到`Viewview`页面。
- b. `同一`被调用页面支持`无限制`跳转来源，即界面显示逻辑不依赖于跳转来源。
- c. `协议内容跨平台`，方面服务器端控制客户端跳转行为。此目标主要用于实现`广告位`、`系统消息`等点击跳转行为多变的场景。
- d. 所有页面跳转都支持，所有页面跳转都可以通过该协议实现跳转。

#### 2. 协议本质

协议的本质是将每一个页面都抽象为一个可调用`接口`，一个接口需要提供给主动调用方（来源）一个调用规则。只要符合调用规则的调用请求都是合法的。

#### 3. 协议设计

- 角色关系

    ```
    调用页面（CallPage）    ---->   PageRoute    ---->    被调用页面（CalledPage）
                                                           |
                                        <----（可选返回）----|
    ```

- 角色定义

    ```
       页面：一个可刷新的区域
    1. 调用页面（CallPage）：调用来源
    2. 被调用页面（CalledPage）：被调用页面，具有以下属性
           pageid: [string]页面资源定位符，
               android例子：wode_shezhi
                           laidian
           pagetype: [string]页面类型，在各个平台的定义为：
               h5：webview
               android：activity, fragment, webview
               ios：viewcontroler, webview
           pageparams: [string]该页面被刷新时需要的参数，格式是`字典类型json`字符串，有以下公共通用参数：
               callsource: [string]具体格式待完善，待确定
               needreturn: [bool]是否需要左上角的返回按钮，待确定
               ...
               ...
    3. PageRoute：页面跳转路由器，根据pageid,pagetype确定被调用页面，带着pageparams参数启动调用。
    
    ```

#### 4. 场景举例（只列举有不同跳转来源的场景）

- 首页广告位跳转到不同页面，每个广告点击后需要的跳转都可能不一样。广告信息一般都由服务器返回，通过返回参数pageaction={pageid:'', pagetype:'', pageparams:''}实现服务器对客户端跳转的控制。
- 系统消息，系统消息类型很多。如某人关注了你，点击消息后跳转到该人主页；如官方发布了活动，点击后跳转到活动主页；如您的订单已被确认发货，点击后跳转到该订单详情等。通过每条消息返回的pageaction={pageid:'', pagetype:'', pageparams:''}实现点击消息跳转的控制。

