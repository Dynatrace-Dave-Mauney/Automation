from OpenSSL import SSL, crypto
import socket

def getPEMFile():

  dst = ('www.google.com', 443)
  ctx = SSL.Context(SSL.SSLv23_METHOD)
  s = socket.create_connection(dst)
  s = SSL.Connection(ctx, s)
  s.set_connect_state()
  s.set_tlsext_host_name(str.encode(dst[0]))

  s.sendall(str.encode('HEAD / HTTP/1.0\n\n'))

  peerCertChain = s.get_peer_cert_chain()
  pemFile = ''

  for cert in peerCertChain:
      pemFile += crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8")

  return pemFile

print(getPEMFile())