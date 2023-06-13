import pyotp
import qrcode
t = pyotp.TOTP('OD4CY5IDEUS7ML72PDC4RBBD5IRPNHQJ')
auth_str = t.provisioning_uri(name="Admin Soiflix", issuer_name="Soiflix")
img = qrcode.make(auth_str)
img.show()
ans = input()
kuy = t.verify(ans)
