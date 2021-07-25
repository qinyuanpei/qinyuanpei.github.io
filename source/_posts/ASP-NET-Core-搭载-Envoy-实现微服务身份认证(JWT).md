---
toc: true
title: ASP.NET Core 搭载 Envoy 实现微服务身份认证(JWT)
categories:
  - 编程语言
tags:
  - 微服务
  - Envoy
  - JWT
  - Keycloak
  - 认证
copyright: true
abbrlink: 731808750
date: 2021-07-25 09:41:24
---
在构建以 gRPC 为核心的微服务架构的过程中，得益于 Envoy 对 gRPC 的“**一等公民**”支持，我们可以在过滤器中对 gRPC 服务进行转码，进而可以像调用 Web API 一样去调用一个 gRPC 服务。通常情况下， RPC 会作为微服务间内部通信的信使，例如，Dubbo、Thrift、gRPC、WCF 等等更多是应用在对内通信上。所以，一旦我们通过 Envoy 将这些 gRPC 服务暴露出来，其性质就会从对内通信变为对外通信。我们知道，对内和对外的接口，无论是安全性还是规范性，都有着相当大的区别。博主从前的公司，对内的 WCF 接口，长年处于一种"**裸奔**"的状态，属于没有授权、没有认证、没有文档的“**三无产品**”。那么，当一个 gRPC 服务通过 Envoy 暴露出来以后，我们如何保证接口的安全性呢？这就是今天这篇博客的主题，即 Envoy 作为网关如何提供身份认证功能，在这里，我们特指通过JWT，即 Json Web Token 来对接口调用方进行身份认证。

# 搭建 Keycloak

对于 [JWT](https://jwt.io) ，即 Json Web Tokn ，我想大家应该都非常熟悉了，它是目前最流行的跨域认证解决方案。考虑到，传统的 Session 机制，在面对集群环境时，扩展性方面表现不佳。在日益服务化、集群化的今天，这种无状态的、轻量级的认证方案，自然越来越受到人们的青睐。在 ASP.NET Core 中整合JWT非常简单，因为有各种第三方库可以帮助你生成令牌，你唯一需要做的就是配置授权/认证中间件，它可以帮你完成令牌校验这个环节的工作。除此以外，你还可以选择更重量级的 [Identity Server 4](https://identityserver4.readthedocs.io/en/latest/)，它提供了更加完整的身份认证解决方案。在今天这篇博客里，我们使用的 [Keycloak](https://www.keycloak.org)，一个类似 Identity Server 4 的产品，它提供了一个更加友好的用户界面，可以更加方便的管理诸如客户端、用户、角色等等信息。其实，如果从头开始写不是不可以，可惜博主一时间无法实现 [JWKS](https://auth0.com/docs/tokens/json-web-tokens/json-web-key-sets)，所以，就请大家原谅在下拾人牙慧，关于 JWKS ，我们会在下一节进行揭晓。接触微服务以来，在做技术选型时，博主的一个关注点是，这个方案是否支持容器化。所以，在这一点上，显然是 Keycloak 略胜一筹，为了安装 Ketcloak ，我们准备了如下的服务编排文件：

```yaml
version: '3'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:14.0.0
    depends_on:
      - postgres
    environment:
      KEYCLOAK_USER: ${KEYCLOAK_USER}
      KEYCLOAK_PASSWORD: ${KEYCLOAK_PASS}
      DB_VENDOR: postgres
      DB_ADDR: postgres
      DB_DATABASE: ${POSTGRESQL_DB}
      DB_USER: ${POSTGRESQL_USER}
      DB_PASSWORD: ${POSTGRESQL_PASS}
    ports:
      - "7070:8080"
  postgres:
    image: postgres:13.2
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRESQL_DB}
      POSTGRES_USER: ${POSTGRESQL_USER}
      POSTGRES_PASSWORD: ${POSTGRESQL_PASS}
```
其中，`.env`文件放置了服务编排文件中使用到的环境变量：

```env
# KEYCLOAK
KEYCLOAK_USER=admin
KEYCLOAK_PASS=admin
# POSTGRESQL
POSTGRESQL_DB=keycloak
POSTGRESQL_USER=keycloak
POSTGRESQL_PASS=keycloak
```

此时，我们运行`docker compose up`命令就可以得到一个 Keycloak 环境，它将作为我们整个微服务里的认证中心，负责对用户、角色、权限、客户端等进行管理。于此同时，接口消费方可以通过 Keycloak 获取令牌、JWKS，而 Envoy 正是利用 JWKS 来对令牌进行校验的。这个 JWKS 到底是何方神圣，我们暂且按下不表。在正式使用 Keycloak 前，我们需要做一点简单的配置工作，具体来说，就是指创建用户、角色和客户端，我们一起来看一下。

首先，是创建一个用户，这里以《天龙八部》中壮志未酬的“**慕容龙城**”为例：

![ Keycloak 创建用户](https://i.loli.net/2021/07/23/U9Pm3HFLn1y6dYB.png)

《天龙八部》中提到，“**慕容龙城**”一心想光复大燕，可惜时不我与，正好遇上宋太祖建立宋朝，即使他创造出“**斗转星移**”的武功绝学，依然免不了郁郁而终的结局。慕容龙城算是第一代创业者，我们准备一个`Developer`的角色：

![ Keycloak 创建角色](https://i.loli.net/2021/07/23/H8xy3BYDz1XmWf9.png)

在权限系统的设计中，角色总是需要和用户关联在一起。同样地，在 Keycloak 中，我们需要给“**慕容龙城**”分配一个`Developer`的角色：

![ Keycloak 分配角色](https://i.loli.net/2021/07/23/ZDui9X3weq5NMs8.png)

到了“**慕容复**”这一代，“**慕容垂**”假借死亡之名秘密活动，而活跃在台前的“**慕容复**”，实际上是作为慕容家族的“**代理人**”出现。在今天这篇文章中，Envoy 会充当认证服务的代理，因为我们希望 Envoy 可以对所有进站的 API 请求进行统一的认证。所以，这里，我们还需要创建一个客户端：`envoy-client`，并为其分配客户端角色：

![ Keycloak 创建客户端](https://i.loli.net/2021/07/23/MJC3dVkE7UxopyO.png)

OK，我们都知道，[OAuth 2.0](https://oauth.net/2/) 有这样四种认证方式：密码模式、客户端模式、简化模式、授权码模式。这四种认证方式如何在 Keycloak 中实现呢？目前，博主基本搞清楚了前面两种。我们在创建完客户端以后，可以通过设置访问类型来决定客户端使用哪种认证方式，目前已知，当访问类型的取值为`public`时，表示密码模式。当访问类型的取值为`confidential`时，表示客户端模式。这里，我们以客户端模式为例：

![ Keycloak 客户端模式](https://i.loli.net/2021/07/23/le5rstobVOh91m3.png)

此时，我们就可以拿到一个重要的信息：`client_secret`，如果大家使用过客户端模式，就会知道它是获取令牌的重要参数之一。好了，当我们有了这些信息以后，该怎么样去获取令牌呢？我们只需要用 POST 的方式，将`grant_type`、`client_id`、`client_secret`、`username`、`password`、`scope`传过去即可：

![从 Keycloak 获取令牌 ](https://i.loli.net/2021/07/23/S5rgmZaGEqQkHUK.png)

如果需要刷新令牌，则只需要再追加一个`refresh_token`参数即可，它是我们第一次获取到的令牌：

![从 Keycloak 刷新令牌](https://i.loli.net/2021/07/23/ukdNami5yMERWDc.png)

可能大家会疑惑，博主是从哪里知道这些 API 的端点地址的呢？其实，和 Identity Server 4 类似， Keycloak 提供了一个用于服务发现的接口地址：`/auth/realms/master/.well-known/openid-configuration`，通过这个接口地址，我们可以获得一份 API 列表：

![ Keycloak 提供的 “服务发现” 能力](https://i.loli.net/2021/07/23/bDYNASUw23qLyml.png)

可以注意到，图中有我们需要的换取令牌的接口，以及提供 JWKS 的接口：`/auth/realms/master/protocol/openid-connect/certs"`，尤其第二点，它对于对我们进行下一个步骤意义重大，Envoy 能不能承担起微服务认证的重担，就看它的啦，至此， Keycloak 的搭建工作已经完成。


# 配置 Envoy

在上一节内容中，博主卖了一个关子，说要等到这一节再说 JWKS 是何方神圣？不过，博主以为，“**饭要一口一口吃，步子迈太大，咔，容易扯着蛋**”，我们还是先来说说 JWT ，因为只要你了解了它的结构，你才能了解如何去检验一个令牌。我们说，JWT，是 JSON Web Token 的简称，那这个 JSON 到底体现在哪里呢？而这要从 JWT 的结构开始说起。

![JSON Web Token 结构说明图](https://i.loli.net/2021/07/23/Tdag82VsSGJxD9u.png)

这是一张来自 [JWT](https://jwt.io/) 官网的截图，博主认为，这张图非常清晰地展示出了 JWT 的加密过程，我们熟悉的这个令牌，其实是由`header`、`payload`和`signature`三个部分组成，其基本格式为：`header.payload.signature`，细心的朋友会发现，图中生成的令牌中含有两个`.`。其中，`header`部分是一个 JSON 对象，表示类型(**typ**)及加密算法(**alg**)，常见的加密算法主要有 HMAC、RSA、ECDSA 三个系列。`payload`部分同样是一个 JSON 对象，主要用来存放实际需要传递的数据。目前，JWT 官方规定了以下7个备选字段：

* iss，即 issuer，表示：令牌签发人
* exp，即 expiration time，表示：令牌过期时间
* sub，即 subject，表示：令牌主题
* aud，即 audience，表示：令牌受众
* nbf，即 Not Before，表示：令牌生效时间
* iat，即 Issued At，表示：令牌签发时间
* jti，即 JWT ID，表示：令牌编号

需要注意的是，`header`和`payload`这两部分，默认是不加密的，这意味着任何人都可以读到这里的信息，所以，一个重要的原则是，不要在`payload`中存放重要的、敏感的信息。无论是`header`还是`payload`，最终都需要通过 [Base64URL](https://www.base64url.com/) 算法将其转化为普通的字符串，该算法和 [Base64](https://www.sojson.com/base64.html) 算法类似，唯一的不同点在于它会对`+`、`/` 和 `=` 这三个符号进行替换，因为这三个符号在网址中有着特殊的含义。

![Base64 & Base64URL 算法对比](https://i.loli.net/2021/07/23/zDx765FpRMaP8mK.png)

第三部分，`signature`，即通常意义上的签名，主要是防止数据篡改。对于 HMAC 系列的加密算法，需要指定一个密钥，以 HMACSHA256 算法为例，其签名函数为：`HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)`。对于 RSA 和 ECDSA 这两个系列的加密算法，需要指定公钥和私钥，以 ECDSASHA512 算法为例，其签名函数为：`ECDSASHA512(base64UrlEncode(header) + "." + base64UrlEncode(payload), PublicKey, PrivateKey)`。一旦计算出签名，就可以将这三部分合成一个令牌，而这就是 JWT 的产生原理，而如果我们对第一节中获得的令牌进行解密，我们就会得到下面的结果：

![解密 Keycloak 生成的令牌](https://i.loli.net/2021/07/23/mpVo8vasYWL4gPN.png)

所以，JSON Web Token 中的 JSON，其实是指 `header` 和 `payload` 这两个 JSON 对象，并且我们可以注意到，Keycloak 中生成的令牌实际上携带了更多的信息，例如，客户端、IP 地址、`realm_access` 以及 `resource_access`等等，所以。 JWT 其实是一个相对宽松的规范，在实现`payload`这部分时，可以结合实际场景做更多的扩展，唯一的要求还是那句话，不要在`payload`中存放重要的、敏感的信息。至此，我们讲清楚了 JWT 的底层原理。

OK，解释清楚了 JWT，我们再来说 JWKS，这位又是何方神圣呢？我们提到，JWT 至少需要一个密钥或者一对公/私钥来进行签名的校验，因为对于`header`和`payload`这两个部分而言，它的加密算法始终都是 Base64URL，所以，我们总是可以反推出原始的 JSON 字符串。接下来，我们只需要按签名函数计算签名即可，对于 HMAC 系列的加密算法，需要指定一个密钥；对于 RSA 和 ECDSA 这两个系列的加密算法，需要指定公钥和私钥。由此，我们就可以计算出一个签名，此时，我们只需要比较两个签名是否一致即可。

![ JWT 校验过程示意图](https://i.loli.net/2021/07/23/N6ybGazKBUSfE2H.png)

通过 JWKS 的 [官网](https://auth0.com/docs/tokens/json-web-tokens/json-web-key-sets)，我们可以了解到一件事情，那就是 JWKS 本质上是 Json Web Key Set 的简称，顾名思义，这是一组可以校验任意 JWT 的公钥，并且这些 JWT 必须是通过 RS256 算法进行签名的，RS256 则是我们上面这张图里的 RSA 非对唱加密算法，它需要一个公钥和一个私钥，通常强况下，私钥用来生成签名，公钥用来校验签名。这个 JWKS 呢？同样是一个 JSON 对象，它只有一个属性`keys`，以 Keycloak 中获得的 JWKS 为例：

![ Keycloak 产生的 JWKS](https://i.loli.net/2021/07/24/lQrXThYCvk9RPLm.png)

 关于 JWKS 的规范，大家可以通过 [RFC7515](https://datatracker.ietf.org/doc/html/rfc7517) 来了解，作为一种通用的规范，Identity Server 4 和 Keycloak 都实现了这一规范，所以，就今天这篇博客而言，不管是哪一种方案，它都可以和 Envoy 配合得天衣无缝。为什么这样说呢？因为我们在 Envoy 中实现 JWT 认证，其核心还是 JWKS 这一套规范。博主没有选择从头开始实现这一切，就在于这个 JWKS 有特别多的细节。总之，我们只需要知道，通过 JWKS 可以对一个令牌进行验证，而 Envoy 刚好有这样一个过滤器，下面是 Envoy 中对应的配置项：

 ```yaml
http_filters:
  - name: envoy.filters.http.jwt_authn
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
      providers:
        jwt_provider:
          issuer: "http://192.168.50.162:7070/auth/realms/master"
          audiences:
            - "account"
          forward: true
          remote_jwks:
            http_uri:
              uri: "http://192.168.50.162:7070/auth/realms/master/protocol/openid-connect/certs"
              cluster: keycloak
              timeout: 5s
      rules:
        - match:
            prefix: "/api/w"
          requires:
            provider_name: jwt_provider
        - match:
            prefix: "/api/c"
          requires:
            provider_name: jwt_provider
  - name: envoy.filters.http.router
 ```

可以注意到，我们这里配置了一个叫做`envoy.filters.http.jwt_authn`的过滤器，并为这个过滤器指定了一个叫做`jwt_provider`的认证提供者，其中的`issuer`和`audiences`，我们在讲解 JWT 结构的时候提到过，最为关键的是`remote_jwks`，我们通过 Keycloak 的服务发现功能，可以获得这个地址，我们将其配置到 Envoy 中即可，Envoy 可以通过它来验证一个 JWT 的令牌，而下面的规则，表示哪些路由需要认证，这里我们假设需要对`/api/w`和`/api/c`这两个端点进行认证。所以，可以预见的是，我们可以为整个网关配置统一的认证流程，无论我们有多少个微服务。以往我们都是通过 ASP.NET Core 里的过滤器来实现应用级的认证服务，而此时此刻，我们有了容器级别的认证服务，基础设施从框架提升到了容器层面。除此以外，我们还需要为 Envoy 定义一个集群，这样读取远程 JWKS 的请求才会被正确地转发过去：

```yaml
clusters:
  - name: keycloak
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: keycloak
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: 192.168.50.162
                port_value: 7070

```
如此，整个认证服务相关的基础设施均已准备就绪，所谓“万事俱备，只欠东风”，我们还需要定义资源 API 供调用者消费，所以，接下来，我们来看看 API 如何编写。

# 编写 API

编写 API 非常简单，我们直接用 ASP.NET Core 创建两个项目即可，这里是两个服务：`CityService` 和 `WeatherService`。

首先，是 `CityService`：

```csharp
[ApiController]
[Route("[controller]")]
public class CityController : ControllerBase
{
    private static readonly string[] Cities = new[]
    {
      "中卫", "西安", "苏州", "安庆", "洛阳", "银川", "兰州"
    };

    private readonly ILogger<CityController> _logger;

    public CityController(ILogger<CityController> logger)
    {
      _logger = logger;
    }

    [HttpGet]
    public dynamic Get()
    {
      var rnd = new Random();
      var city =  Cities[rnd.Next(Cities.Length)];
      return new { City = city, Now = DateTime.Now };
    }
}
```

接下来，是 `WeatherService`：

```csharp
[ApiController]
[Route("[controller]")]
public class WeatherController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
      "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private readonly ILogger<WeatherController> _logger;

    public WeatherController(ILogger<WeatherController> logger)
    {
      _logger = logger;
    }

    [HttpGet]
    public IEnumerable<WeatherForecast> Get()
    {
      var rng = new Random();
      return Enumerable.Range(1, 5).Select(index => new WeatherForecast
      {
        Date = DateTime.Now.AddDays(index),
        TemperatureC = rng.Next(-20, 55),
        Summary = Summaries[rng.Next(Summaries.Length)]
      })
      .ToArray();
    }
}
```
关于这两个服务如何实现容器化、反向代理等等的细节，大家可以参考博主前面几篇文章，本文示例已托管到 [Github](https://hub.fastgit.org/Regularly-Archive/2021/tree/master/src/EnvoyJwt)，供大家做进一步的参考。


# 服务编排

这段时间最大的收获便是，学会了通过`docker-compose`对服务进行编排，虽然目前还有点悬而未决的东西，可一旦接触了这种略显“**高端**”的技巧，便再不愿回到刀耕火种、敲命令行维护`docker`环境的时代。等有时间了，博主会考虑写一点`docker`或者`docker-compose`使用技巧的文章，当然这些都是以后的事情啦！我们要活在当下啊，还是看看这个`docker-compose.yaml`文件：

```yaml
version: '3'
services:
  envoy_gateway:
    build: Envoy/
    ports:
      - "6060:9090"
      - "6061:9091"
    volumes:
      - ./Envoy/envoy.yaml:/etc/envoy/envoy.yaml
  city_service:
    build: CityService/
    ports:
      - "8081:80"![Envoy-Jwt-Keycloak-16.png](https://i.loli.net/2021/07/24/rCcUBWDyJVtOxkd.png)
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
  weather_service:
    build: WeatherService/
    ports:
      - "8082:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
  keycloak:
    image: quay.io/keycloak/keycloak:14.0.0
    depends_on:
      - postgres
    environment:
      KEYCLOAK_USER: ${KEYCLOAK_USER}
      KEYCLOAK_PASSWORD: ${KEYCLOAK_PASS}
      DB_VENDOR: postgres
      DB_ADDR: postgres
      DB_DATABASE: ${POSTGRESQL_DB}
      DB_USER: ${POSTGRESQL_USER}
      DB_PASSWORD: ${POSTGRESQL_PASS}
    ports:
      - "7070:8080"
  postgres:
    image: postgres:13.2
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRESQL_DB}
      POSTGRES_USER: ${POSTGRESQL_USER}
      POSTGRES_PASSWORD: ${POSTGRESQL_PASS}
```

等所有的服务都启动起来以后，我们来验证下这个网关，是不是真的像我们期待的那样。注意到，Envoy 对外暴露出来的端口是`6060`，这里我们以`CItyService`为例：

首先，是不带令牌直接访问接口，我们发现接口返回了`401`状态码，并提示：**Jwt is missing**。

![ 不携带令牌，Envoy 认证失败](https://i.loli.net/2021/07/24/Bg5r8dAIbEp4eFy.png)

我们带上令牌会怎么样呢？可以注意到，接口成功地返回了数据，这表示我们的目的达到了，这些经由 Envoy 代理的 API 接口，今后都必须携带令牌进行访问：

![携带令牌，Envoy 返回数据](https://i.loli.net/2021/07/24/rCcUBWDyJVtOxkd.png)

因为 Keycloak 这个认证中心是独立于我们的应用单独存在的，所以，我们可以直接在 Keycloak 中设置令牌的过期时间、为用户分配角色、为不同的资源设置范围等等，而这一切都不需要应用程序或者 Envoy 做任何调整，开发者只需要认真地写好每一个后端服务即可，这是否就是传说中的基础设施即服务呢？


# 本文小结

本文主要分享了如何利用 Envoy 实现容器级别的 JWT 认证服务，在实现过程中，我们分别了解了 JWT 和 JWKS 这两个概念。其中，JWT 即JSON Web Token，是目前最为流行的跨域认证方案，一个 JWT 通常由 `header`、`payload` 和 `signature` 三个部分组成，JWT 的 JSON 主要体现在`header`和`payload`这两个 JSON 对象上，通过 Base64Url 算法实现串化，而 `signature` 部分则是由`header`和`payload`按照签名函数进行生成，主要目的是防止数据篡改。JWKS 可以利用密钥或者公/私钥对令牌进行验证，利用这一原理，Envoy 中集成了 JWKS ，它表示一组可以校验任意 JWT 的公钥，同样是一个 JSON 对象。为了获得可用的 JWKS，我们可以通过 Identity Server 4 或者 Keycloak 中提供的地址来获得这一信息，方便起见，本文选择了更为便捷的 Keycloak。最终，我们实现了一个通用的、容器级别的认证网关，调用方在消费这些 API 资源时都必须带上从认证中心获得的令牌，进而达到保护 API 资源的目的，更好地保障系统和软件安全。
