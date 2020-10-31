---
layout: default
---
![Octocat](https://springdoc.org/assets/images/springdoc-openapi.png)

# **Introduction**

springdoc-openapi java library helps automating the generation of API documentation using spring boot projects.
springdoc-openapi works by examining an application at runtime to infer API semantics based on spring configurations, class structure and various annotations.

Automatically generates documentation in JSON/YAML and HTML format APIs. 
This documentation can be completed by comments using swagger-api annotations.

This library supports:
*  OpenAPI 3
*  Spring-boot (v1 and v2)
*  JSR-303, specifically for @NotNull, @Min, @Max, and @Size.
*  Swagger-ui
*  OAuth 2

The following video introduces the Library:

[![Watch the video](https://springdoc.org/assets/images/springdoc-openapi-prez.gif)](https://youtu.be/utRxyPfFlDw)

This is a community-based project, not maintained by the Spring Framework Contributors (Pivotal).

# **Getting Started**
![overview](https://springdoc.org/assets/images/common.jpg)

## Integration between spring-boot and swagger-ui 
*   Automatically deploys swagger-ui to a spring-boot application
*   Documentation will be available in HTML format, using the official [swagger-ui jars](https://github.com/swagger-api/swagger-ui.git).
*   The Swagger UI page should then be available at http://server:port/context-path/swagger-ui.html and the OpenAPI description will be available at the following url for json format: http://server:port/context-path/v3/api-docs
    * server: The server name or IP
    * port: The server port
    * context-path: The context path of the application
*   Documentation can be available in yaml format as well, on the following path : /v3/api-docs.yml
*   Add the library to the list of your project dependencies (No additional configuration is needed)

```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-ui</artifactId>
      <version>1.4.8</version>
   </dependency>
```
*   This step is optional: For custom path of the swagger documentation in HTML format, add a custom springdoc property, in your spring-boot configuration file:

```properties
# swagger-ui custom path
springdoc.swagger-ui.path=/swagger-ui.html
```

## Integration of the library in a spring-boot project without the swagger-ui:
*   Documentation will be available at the following url for json format: http://server:port/context-path/v3/api-docs
    * server: The server name or IP
    * port: The server port
    * context-path: The context path of the application
*   Documentation will be available in yaml format as well, on the following path : /v3/api-docs.yml
*   Add the library to the list of your project dependencies. (No additional configuration is needed)

```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-webmvc-core</artifactId>
      <version>1.4.8</version>
   </dependency>
```
*   This step is optional: For custom path of the OpenAPI documentation in Json format, add a custom springdoc property, in your spring-boot configuration file:

```properties
# /api-docs endpoint custom path
springdoc.api-docs.path=/api-docs
```

*   For WildFly users, you need to add the following dependency to make the swagger-ui work:

```xml
   <dependency>
	  <groupId>org.webjars</groupId>
	  <artifactId>webjars-locator-jboss-vfs</artifactId>
	  <version>0.1.0</version>
   </dependency>
```

# **Additional settings**

## Adding API Information and Security documentation
  The library uses spring-boot application auto-configured packages to scan for the following annotations in spring beans: OpenAPIDefinition and Info.
  These annotations declare, API Information: Title, version, licence, security, servers, tags, security and externalDocs.
  For better performance of documentation generation, declare @OpenAPIDefinition and @SecurityScheme annotations within a spring managed bean.  
 
## Error Handling for REST using @ControllerAdvice
To generate documentation automatically, make sure all the methods declare the HTTP Code responses using the annotation: @ResponseStatus

## Disabling the springdoc-openapi endpoints
In order to disable the springdoc-openapi endpoint (/v3/api-docs by default) use the following property:
```properties
# Disabling the /v3/api-docs enpoint
springdoc.api-docs.enabled=false
```

## Disabling the swagger-ui
In order to disable the swagger-ui, use the following property:
```properties
# Disabling the swagger-ui
springdoc.swagger-ui.enabled=false
```
## Swagger-ui configuration
The library supports the swagger-ui official properties:
- [https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/)

You need to declare swagger-ui properties as spring-boot properties.
All these properties should be declared with the following prefix: **springdoc.swagger-ui**

## Selecting the Rest Controllers to include in the documentation 
Additionally to @Hidden annotation from swagger-annotations, its possible to restrict the generated OpenAPI description using package or path configuration.

For the list of packages to include, use the following property:
```properties
# Packages to include
springdoc.packagesToScan=com.package1, com.package2
```

For the list of paths to include, use the following property:
```properties
# Paths to include
springdoc.pathsToMatch=/v1, /api/balance/**
```

## Spring-webflux support with Annotated Controllers
*   Documentation can be available in yaml format as well, on the following path : /v3/api-docs.yml
*   Add the library to the list of your project dependencies (No additional configuration is needed)

```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-webflux-ui</artifactId>
      <version>1.4.8</version>
   </dependency>
```
*   This step is optional: For custom path of the swagger documentation in HTML format, add a custom springdoc property, in your spring-boot configuration file:

```properties
# swagger-ui custom path
springdoc.swagger-ui.path=/swagger-ui.html
```


## Spring-webflux/WebMvc.fn with Functional Endpoints
Since version v1.3.8, the support of functional endpoints has been added.
Two main annotations have been added for this purpose: @RouterOperations and @RouterOperation.

Only REST APIs with the @RouterOperations and @RouterOperation can be displayed on the swagger-ui.

*   @RouterOperation: It can be used alone, if the Router bean contains one single route related to the REST API..
    When using @RouterOperation, its not mandatory to fill the path
	
*   @RouterOperation, can reference directly a spring Bean (beanClass property) and the underlying method (beanMethod property): Springdoc-openapi, will then inspect this method and the swagger annotations on this method level.

```java	
@Bean
@RouterOperation(beanClass = EmployeeService.class, beanMethod = "findAllEmployees")
RouterFunction<ServerResponse> getAllEmployeesRoute() {
	return route(GET("/employees").and(accept(MediaType.APPLICATION_JSON)),
			req -> ok().body(
					employeeService().findAllEmployees(), Employee.class));
}
```
	
*   @RouterOperation, contains the @Operation annotation.
	The @Operation annotation can also be placed on the bean method level if the property beanMethod is declared.
    
*   Don't forget to set **operationId** which is **mandatory**.

```java	
@Bean
@RouterOperation(operation = @Operation(operationId = "findEmployeeById", summary = "Find purchase order by ID", tags = { "MyEmployee" },
		parameters = { @Parameter(in = ParameterIn.PATH, name = "id", description = "Employee Id") },
		responses = { @ApiResponse(responseCode = "200", description = "successful operation", content = @Content(schema = @Schema(implementation = Employee.class))),
				@ApiResponse(responseCode = "400", description = "Invalid Employee ID supplied"),
				@ApiResponse(responseCode = "404", description = "Employee not found") }))
RouterFunction<ServerResponse> getEmployeeByIdRoute() {
	return route(GET("/employees/{id}"),
			req -> ok().body(
					employeeRepository().findEmployeeById(req.pathVariable("id")), Employee.class));
}
```
	
*   @RouterOperations: This annotation should be used if the Router bean contains multiple routes.
    When using RouterOperations, its mandatory to fill the path property. 
	
*   A @RouterOperations, contains many @RouterOperation.

```java	
@RouterOperations({ @RouterOperation(path = "/getAllPersons", beanClass = PersonService.class, beanMethod = "getAll"),
		@RouterOperation(path = "/getPerson/{id}", beanClass = PersonService.class, beanMethod = "getById"),
		@RouterOperation(path = "/createPerson", beanClass = PersonService.class, beanMethod = "save"),
		@RouterOperation(path = "/deletePerson/{id}", beanClass = PersonService.class, beanMethod = "delete") })
@Bean
public RouterFunction<ServerResponse> personRoute(PersonHandler handler) {
	return RouterFunctions
			.route(GET("/getAllPersons").and(accept(MediaType.APPLICATION_JSON)), handler::findAll)
			.andRoute(GET("/getPerson/{id}").and(accept(MediaType.APPLICATION_STREAM_JSON)), handler::findById)
			.andRoute(POST("/createPerson").and(accept(MediaType.APPLICATION_JSON)), handler::save)
			.andRoute(DELETE("/deletePerson/{id}").and(accept(MediaType.APPLICATION_JSON)), handler::delete);
}
```
	
All the documentations filled using @RouterOperation, might be completed by the router function data. 
For that, @RouterOperation fields must help identify uniquely the concerned route.
springdoc-openpi scans for a unique route related to a @RouterOperation annotation, using on the following criteria:
- by path
- by path and RequestMethod
- by path and produces
- by path and consumes
- by path and RequestMethod and produces
- by path and RequestMethod and consumes
- by path and produces and consumes
- by path and RequestMethod and produces and consumes

Some code samples are available on GITHUB of demos:

- [Sample application with Functional Endpoints documentation](https://github.com/springdoc/springdoc-openapi-demos/tree/master/springdoc-openapi-spring-boot-2-webflux-functional)

And some of the project tests: (from app69 to app75)

- [Sample code with Functional Endpoints documentation](https://github.com/springdoc/springdoc-openapi/tree/master/springdoc-openapi-webflux-core/src/test/java/test/org/springdoc/api)

## Spring Hateoas support
The support for Spring Hateoas is available using the dependency springdoc-openapi-hateoas.
The projects that use Spring Hateoas should combine this dependency with the springdoc-openapi-ui dependency.
This dependency enables the support of Spring Hateoas format.
```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-hateoas</artifactId>
      <version>1.4.8</version>
   </dependency>
```

## Spring Data Rest support
The support for Pageable of spring-data-commons is available.
If only want to enable the support of spring Pageable Type, you can just enable it using:

```java
SpringDocUtils.getConfig().replaceWithClass(org.springframework.data.domain.Pageable.class, 
org.springdoc.core.converters.models.Pageable.class);
```

Alternately, the projects that use Pageable type can aslo add the follwing dependency together with the springdoc-openapi-ui dependency.
This dependency enables the support of spring-data-rest types as well: @RepositoryRestResource and QuerydslPredicate annotations.
```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-data-rest</artifactId>
      <version>1.4.8</version>
   </dependency>
```

## Spring security support
For a project that uses spring-security, you should add the following dependency, together with the springdoc-openapi-ui dependency:
This dependency helps ignoring @AuthenticationPrincipal in case its used on REST Controllers.
```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-security</artifactId>
      <version>1.4.8</version>
   </dependency>
```

## Kotlin support
For a project that uses Kotlin, you should add the following dependency.
This dependency improves the support of Kotlin types:
```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-kotlin</artifactId>
      <version>1.4.8</version>
   </dependency>
```
- If your are using spring-web, you combine the springdoc-openapi-kotlin module with springdoc-openapi-ui.
- If your are using spring-webflux, you combine the springdoc-openapi-kotlin module  with springdoc-openapi-webflux-ui.

## Groovy support
For a project that uses Groovy, you should add the following dependency, together with the springdoc-openapi-ui dependency:
This dependency improves the support of Kotlin types:
```xml
   <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-groovy</artifactId>
      <version>1.4.8</version>
   </dependency>
```


## Introduction to springdoc-openapi-maven-plugin

The aim of springdoc-openapi-maven-plugin is to generate json and yaml OpenAPI description  during build time. 
The plugin works during integration-tests phase, and generate the OpenAPI description. 
The plugin works in conjunction with spring-boot-maven plugin. 

You can test it during the integration tests phase using the maven command:

```protobuf
mvn verify
```

In order to use this functionality, you need to add the plugin declaration on the plugins section of your pom.xml:

```xml
<plugin>
 <groupId>org.springframework.boot</groupId>
 <artifactId>spring-boot-maven-plugin</artifactId>
 <version>2.3.4.RELEASE</version>
 <configuration>
    <jvmArguments>-Dspring.application.admin.enabled=true</jvmArguments>
 </configuration>
 <executions>
  <execution>
   <id>pre-integration-test</id>
   <goals>
    <goal>start</goal>
   </goals>
  </execution>
  <execution>
   <id>post-integration-test</id>
   <goals>
    <goal>stop</goal>
   </goals>
  </execution>
 </executions>
</plugin>
<plugin>
 <groupId>org.springdoc</groupId>
 <artifactId>springdoc-openapi-maven-plugin</artifactId>
 <version>1.1</version>
 <executions>
  <execution>
   <id>integration-test</id>
   <goals>
    <goal>generate</goal>
   </goals>
  </execution>
 </executions>
</plugin>
```

For more custom settings of the springdoc-openapi-maven-plugin, you can consult the plugin documentation:
- [https://github.com/springdoc/springdoc-openapi-maven-plugin](https://github.com/springdoc/springdoc-openapi-maven-plugin)

## Introduction to springdoc-openapi-gradle-plugin

This plugin allows you to generate an OpenAPI 3 specification for a Spring Boot application from a Gradle build. 

```groovy
plugins {
      id("org.springframework.boot") version "2.3.0.RELEASE"
      id("com.github.johnrengelman.processes") version "0.5.0"
      id("org.springdoc.openapi-gradle-plugin") version "1.3.0"
}
```

When you add this plugin and its runtime dependency plugins to your build file, the plugin creates the following tasks:
- forkedSpringBootRun
- generateOpenApiDocs

```slim
gradle clean generateOpenApiDocs
```

For more custom configuration of springdoc-openapi-gradle-plugin ,you can consult the plugin documentation:
- [https://github.com/springdoc/springdoc-openapi-gradle-plugin](https://github.com/springdoc/springdoc-openapi-gradle-plugin)

# **springdoc applications demos**

## [Demo Spring Boot 2 Web MVC with OpenAPI 3](http://158.101.164.60:8081/).
## [Demo Spring Boot 2 WebFlux with OpenAPI 3](http://158.101.164.60:8082/).
## [Demo Spring Boot 1 Web MVC with OpenAPI 3](http://158.101.164.60:8083/).
## [Demo Spring Boot 2 WebFlux with Functional endpoints OpenAPI 3](http://158.101.164.60:8084/swagger-ui.html).
## [Demo Spring Boot 2 and Spring Hateoas with OpenAPI 3](http://158.101.164.60:8085/swagger-ui.html).

![Branching](https://springdoc.org/assets/images/pets.png)

## Source code of the Demo Applications
*   [https://github.com/springdoc/springdoc-openapi-demos.git](https://github.com/springdoc/springdoc-openapi-demos.git)

## Dependencies repository

The springdoc-openapi libraries are hosted on maven central repository. 
The artifacts can be viewed accessed at the following locations:

Releases:
* [https://oss.sonatype.org/content/groups/public/org/springdoc/](https://oss.sonatype.org/content/groups/public/org/springdoc/).

Snapshots:
* [https://oss.sonatype.org/content/repositories/snapshots/org/springdoc/](https://oss.sonatype.org/content/repositories/snapshots/org/springdoc/).

# **Thank you for the support**

* Thanks a lot [JetBrains](https://www.jetbrains.com/?from=springdoc-openapi) for supporting springdoc-openapi project.

![Octocat](https://springdoc.org/assets/images/jetbrains.svg)
