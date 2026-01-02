Name:           maven-resolver
Epoch:          1
Version:        1.9.24
Release:        1
Summary:        Apache Maven Artifact Resolver library
License:        Apache-2.0
URL:            https://maven.apache.org/resolver/
BuildArch:      noarch

Source0:        https://archive.apache.org/dist/maven/resolver/maven-resolver-%{version}-source-release.zip

Patch:          0001-Remove-use-of-deprecated-SHA-1-and-MD5-algorithms.patch
Patch:          0002-Make-I-O-errors-during-test-cleanup-non-fatal.patch

BuildRequires:  javapackages-bootstrap

Provides:       maven-resolver-api = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-connector-basic = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-impl = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-spi = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-transport-classpath = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-transport-file = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-transport-http = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-transport-wagon = %{epoch}:%{version}-%{release}
Provides:       maven-resolver-util = %{epoch}:%{version}-%{release}

%description
Apache Maven Artifact Resolver is a library for working with artifact
repositories and dependency resolution. Maven Artifact Resolver deals with the
specification of local repository, remote repository, developer workspaces,
artifact transports and artifact resolution.

%prep
%autosetup -p1 -C

# Skip tests that equire internet connection
rm maven-resolver-supplier/src/test/java/org/eclipse/aether/supplier/RepositorySystemSupplierTest.java
rm maven-resolver-transport-http/src/test/java/org/eclipse/aether/transport/http/{HttpServer,HttpTransporterTest}.java
%pom_remove_dep org.eclipse.jetty: maven-resolver-transport-http

%pom_remove_plugin -r :bnd-maven-plugin
%pom_remove_plugin -r org.codehaus.mojo:animal-sniffer-maven-plugin
%pom_remove_plugin -r :japicmp-maven-plugin
%pom_remove_plugin -r :maven-enforcer-plugin

%pom_disable_module maven-resolver-demos
%pom_disable_module maven-resolver-named-locks-hazelcast
%pom_disable_module maven-resolver-named-locks-redisson
%pom_disable_module maven-resolver-transport-classpath
%mvn_package :maven-resolver-test-util __noinstall

# generate OSGi manifests
for pom in $(find -mindepth 2 -name pom.xml) ; do
  %pom_add_plugin "org.apache.felix:maven-bundle-plugin" $pom \
  "<configuration>
    <instructions>
      <Bundle-SymbolicName>\${project.groupId}$(sed 's:./maven-resolver::;s:/pom.xml::;s:-:.:g' <<< $pom)</Bundle-SymbolicName>
      <Export-Package>!org.eclipse.aether.internal*,org.eclipse.aether*</Export-Package>
      <_nouses>true</_nouses>
    </instructions>
  </configuration>
  <executions>
    <execution>
      <id>create-manifest</id>
      <phase>process-classes</phase>
      <goals><goal>manifest</goal></goals>
    </execution>
  </executions>"
done
%pom_add_plugin "org.apache.maven.plugins:maven-jar-plugin" pom.xml \
"<configuration>
  <archive>
    <manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
  </archive>
</configuration>"

%mvn_alias 'org.apache.maven.resolver:maven-resolver{*}' 'org.eclipse.aether:aether@1'
%mvn_alias 'org.apache.maven.resolver:maven-resolver-transport-wagon' 'org.eclipse.aether:aether-connector-wagon'
%mvn_file ':maven-resolver{*}' %{name}/maven-resolver@1 aether/aether@1

%build
%mvn_build -j

%install
%mvn_install

%files -f .mfiles
%license LICENSE NOTICE
