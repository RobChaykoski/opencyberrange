function fn() {
  var baseUrl = karate.properties['baseUrl'] || 'http://127.0.0.1:18000';
  var fixturePath = karate.properties['fixturePath'] || 'target/security-fixture.json';
  var Files = Java.type('java.nio.file.Files');
  var Paths = Java.type('java.nio.file.Paths');
  var StandardCharsets = Java.type('java.nio.charset.StandardCharsets');
  var bytes = Files.readAllBytes(Paths.get(fixturePath));
  var text = new java.lang.String(bytes, StandardCharsets.UTF_8);
  var fixture = JSON.parse(String(text));

  karate.configure('connectTimeout', 5000);
  karate.configure('readTimeout', 20000);
  karate.configure('logPrettyRequest', false);
  karate.configure('logPrettyResponse', false);

  return {
    baseUrl: baseUrl,
    fixture: fixture,
    uploadNotAZip: Paths.get('fixtures/not-a-zip.zip').toAbsolutePath().toString(),
    uploadNonMd: Paths.get('fixtures/non-md.zip').toAbsolutePath().toString(),
    uploadValid: Paths.get('fixtures/valid.zip').toAbsolutePath().toString()
  };
}
