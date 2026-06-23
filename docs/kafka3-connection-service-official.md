# Kafka3ConnectionService 2.10.0

Source: https://nifi.apache.org/components/org.apache.nifi.kafka.service.Kafka3ConnectionService/
Source type: Official Apache NiFi component documentation

Kafka3ConnectionService 2.10.0
  Bundle org.apache.nifi | nifi-kafka-3-service-nar Description Provides and manages connections to Kafka Brokers for producer or consumer operations. Tags Apache, Consume, Kafka, Message, Publish Input Requirement   Supports Sensitive Dynamic Properties false

Properties

-   Acknowledgment Wait Time
After sending a message to Kafka, this indicates the amount of time that the service will wait for a response from Kafka. If Kafka does not acknowledge the message within this time period, the service will throw an exception.

  Display Name Acknowledgment Wait Time Description After sending a message to Kafka, this indicates the amount of time that the service will wait for a response from Kafka. If Kafka does not acknowledge the message within this time period, the service will throw an exception.  API Name ack.wait.time Default Value 5 sec Expression Language Scope Not Supported Sensitive false Required true

-   Bootstrap Servers
Comma-separated list of Kafka Bootstrap Servers in the format host:port. Corresponds to Kafka bootstrap.servers property

  Display Name Bootstrap Servers Description Comma-separated list of Kafka Bootstrap Servers in the format host:port. Corresponds to Kafka bootstrap.servers property API Name bootstrap.servers Expression Language Scope Not Supported Sensitive false Required true

-   Client Timeout
Default timeout for Kafka client operations. Mapped to Kafka default.api.timeout.ms. The Kafka request.timeout.ms property is derived from half of the configured timeout

  Display Name Client Timeout Description Default timeout for Kafka client operations. Mapped to Kafka default.api.timeout.ms. The Kafka request.timeout.ms property is derived from half of the configured timeout API Name default.api.timeout.ms Default Value 60 sec Expression Language Scope Not Supported Sensitive false Required true

-   Transaction Isolation Level
Specifies how the service should handle transaction isolation levels when communicating with Kafka. The uncommited option means that messages will be received as soon as they are written to Kafka but will be pulled, even if the producer cancels the transactions. The committed option configures the service to not receive any messages for which the producer's transaction was canceled, but this can result in some latency since the consumer must wait for the producer to finish its entire transaction instead of pulling as the messages become available. Corresponds to Kafka isolation.level property.

  Display Name Transaction Isolation Level Description Specifies how the service should handle transaction isolation levels when communicating with Kafka. The uncommited option means that messages will be received as soon as they are written to Kafka but will be pulled, even if the producer cancels the transactions. The committed option configures the service to not receive any messages for which the producer's transaction was canceled, but this can result in some latency since the consumer must wait for the producer to finish its entire transaction instead of pulling as the messages become available. Corresponds to Kafka isolation.level property.  API Name isolation.level Default Value read_committed Allowable Values
-  Read Committed
-  Read Uncommitted    Expression Language Scope Not Supported Sensitive false Required true

-   Kerberos User Service
Service supporting user authentication with Kerberos

  Display Name Kerberos User Service Description Service supporting user authentication with Kerberos API Name kerberos-user-service Service Interface org.apache.nifi.kerberos.SelfContainedKerberosUserService Service Implementations
org.apache.nifi.kerberos.KerberosKeytabUserService

org.apache.nifi.kerberos.KerberosTicketCacheUserService
  Expression Language Scope Not Supported Sensitive false Required true Dependencies
-  SASL Mechanism is set to any of  [GSSAPI]

-   Max Metadata Wait Time
The amount of time publisher will wait to obtain metadata or wait for the buffer to flush during the 'send' call before failing the entire 'send' call. Corresponds to Kafka max.block.ms property

  Display Name Max Metadata Wait Time Description The amount of time publisher will wait to obtain metadata or wait for the buffer to flush during the 'send' call before failing the entire 'send' call. Corresponds to Kafka max.block.ms property  API Name max.block.ms Default Value 5 sec Expression Language Scope Environment variables defined at JVM level and system properties Sensitive false Required true

-   Max Poll Records
Maximum number of records Kafka should return in a single poll.

  Display Name Max Poll Records Description Maximum number of records Kafka should return in a single poll. API Name max.poll.records Default Value 10000 Expression Language Scope Not Supported Sensitive false Required true

-   OAuth2 Access Token Provider Service
Service providing OAuth2 Access Tokens for authentication

  Display Name OAuth2 Access Token Provider Service Description Service providing OAuth2 Access Tokens for authentication API Name oauth2-access-token-provider-service Service Interface org.apache.nifi.oauth2.OAuth2AccessTokenProvider Service Implementations
org.apache.nifi.oauth2.JWTBearerOAuth2AccessTokenProvider

org.apache.nifi.oauth2.StandardOauth2AccessTokenProvider
  Expression Language Scope Not Supported Sensitive false Required true Dependencies
-  SASL Mechanism is set to any of  [OAUTHBEARER]

-   Kerberos Service Name
The service name that matches the primary name of the Kafka server configured in the broker JAAS configuration

  Display Name Kerberos Service Name Description The service name that matches the primary name of the Kafka server configured in the broker JAAS configuration API Name sasl.kerberos.service.name Expression Language Scope Environment variables defined at JVM level and system properties Sensitive false Required true Dependencies
-  SASL Mechanism is set to any of  [GSSAPI]

-   SASL Mechanism
SASL mechanism used for authentication. Corresponds to Kafka Client sasl.mechanism property

  Display Name SASL Mechanism Description SASL mechanism used for authentication. Corresponds to Kafka Client sasl.mechanism property API Name sasl.mechanism Default Value GSSAPI Allowable Values
-  GSSAPI
-  PLAIN
-  SCRAM-SHA-256
-  SCRAM-SHA-512
-  OAUTHBEARER    Expression Language Scope Not Supported Sensitive false Required true Dependencies
-  Security Protocol is set to any of  [SASL_PLAINTEXT, SASL_SSL]

-   SASL Password
Password provided with configured username when using PLAIN or SCRAM SASL Mechanisms

  Display Name SASL Password Description Password provided with configured username when using PLAIN or SCRAM SASL Mechanisms API Name sasl.password Expression Language Scope Environment variables defined at JVM level and system properties Sensitive true Required true Dependencies
-  SASL Mechanism is set to any of  [PLAIN, SCRAM-SHA-256, SCRAM-SHA-512]

-   SASL Username
Username provided with configured password when using PLAIN or SCRAM SASL Mechanisms

  Display Name SASL Username Description Username provided with configured password when using PLAIN or SCRAM SASL Mechanisms API Name sasl.username Expression Language Scope Environment variables defined at JVM level and system properties Sensitive false Required true Dependencies
-  SASL Mechanism is set to any of  [PLAIN, SCRAM-SHA-256, SCRAM-SHA-512]

-   Security Protocol
Security protocol used to communicate with brokers. Corresponds to Kafka Client security.protocol property

  Display Name Security Protocol Description Security protocol used to communicate with brokers. Corresponds to Kafka Client security.protocol property API Name security.protocol Default Value PLAINTEXT Allowable Values
-  PLAINTEXT
-  SSL
-  SASL_PLAINTEXT
-  SASL_SSL    Expression Language Scope Not Supported Sensitive false Required true

-   SSL Context Service
Service supporting SSL communication with Kafka brokers

  Display Name SSL Context Service Description Service supporting SSL communication with Kafka brokers API Name SSL Context Service Service Interface org.apache.nifi.ssl.SSLContextProvider Service Implementations
org.apache.nifi.ssl.PEMEncodedSSLContextProvider

org.apache.nifi.ssl.StandardRestrictedSSLContextService

org.apache.nifi.ssl.StandardSSLContextService
  Expression Language Scope Not Supported Sensitive false Required false Dependencies
-  Security Protocol is set to any of  [SASL_SSL, SSL]

Dynamic Properties

-   The name of a Kafka configuration property or a SASL extension property.
Kafka configuration properties will be added on the Kafka configuration after loading any provided configuration properties. In the event a dynamic property represents a property that was already set, its value will be ignored and WARN message logged. For the list of available Kafka properties please refer to: http://kafka.apache.org/documentation.html#configuration. SASL extension properties can be specified in sasl_extension_propertyName format (e.g. sasl_extension_logicalCluster).

  Name The name of a Kafka configuration property or a SASL extension property. Description Kafka configuration properties will be added on the Kafka configuration after loading any provided configuration properties. In the event a dynamic property represents a property that was already set, its value will be ignored and WARN message logged. For the list of available Kafka properties please refer to: http://kafka.apache.org/documentation.html#configuration. SASL extension properties can be specified in sasl_extension_propertyName format (e.g. sasl_extension_logicalCluster). Value The value of the given property. Expression Language Scope ENVIRONMENT
