from cryptography.hazmat.primitives.serialization import load_pem_private_key
from securesystemslib.signer import CryptoSigner
from in_toto.models.layout import Layout
from in_toto.models.metadata import Envelope
from in_toto.models._signer import load_public_key_from_file
def main():
  # Load martin's private key to later sign the layout
  with open("../keys/martin", "rb") as f:
    key_martin = load_pem_private_key(f.read(), None)

  signer_martin = CryptoSigner(key_martin)
  # Fetch and load jaja's and Manu's public keys
  # to specify that they are authorized to perform certain step in the layout
  key_jaja  = load_public_key_from_file("../functionary_jaja/jaja.pub")
  key_manu  = load_public_key_from_file("../functionary_manu/manu.pub")  

  layout = Layout.read({
      "_type": "layout",
      "keys": {
          key_jaja["keyid"]: key_jaja,
          key_manu["keyid"]: key_manu,
      },
      "steps": [{
          "name": "clone",
          "expected_materials": [],
          "expected_products": [["CREATE", "demo-reference-for-in-toto/security-guild-rocks.py"], ["DISALLOW", "*"]],
          "pubkeys": [key_jaja["keyid"]],
          "expected_command": [
              "git",
              "clone",
              "https://github.com/littlesvensson/demo-reference-for-in-toto.git"
          ],
          "threshold": 1,
        },{
          "name": "update-version",
          "expected_materials": [["MATCH", "demo-reference-for-in-toto/*", "WITH", "PRODUCTS",
                                "FROM", "clone"], ["DISALLOW", "*"]],
          "expected_products": [["MODIFY", "demo-reference-for-in-toto/security-guild-rocks.py"], ["DISALLOW", "*"]],
          "pubkeys": [key_jaja["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "package",
          "expected_materials": [
            ["MATCH", "demo-reference-for-in-toto/*", "WITH", "PRODUCTS", "FROM",
             "update-version"], ["DISALLOW", "*"],
          ],
          "expected_products": [
              ["CREATE", "demo-reference-for-in-toto.tar.gz"], ["DISALLOW", "*"],
          ],
          "pubkeys": [key_manu["keyid"]],
          "expected_command": [
              "tar",
              "--exclude",
              ".git",
              "-zcvf",
              "demo-reference-for-in-toto.tar.gz",
              "demo-reference-for-in-toto",
          ],
          "threshold": 1,
        }],
      "inspect": [{
          "name": "untar",
          "expected_materials": [
              ["MATCH", "demo-reference-for-in-toto.tar.gz", "WITH", "PRODUCTS", "FROM", "package"],

              ["ALLOW", ".keep"],
              ["ALLOW", "martin.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          "expected_products": [
              ["MATCH", "demo-reference-for-in-toto/security-guild-rocks.py", "WITH", "PRODUCTS", "FROM", "update-version"],
              ["ALLOW", "demo-reference-for-in-toto/.git/*"],
              ["ALLOW", "demo-reference-for-in-toto.tar.gz"],
              ["ALLOW", ".keep"],
              ["ALLOW", "martin.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          "run": [
              "tar",
              "xzf",
              "demo-reference-for-in-toto.tar.gz",
          ]
        }],
  })

  metadata = Envelope.from_signable(layout)

  # Sign and dump layout to "root.layout"
  metadata.create_signature(signer_martin)
  metadata.dump("root.layout")
  print('Created demo in-toto layout as "root.layout".')

if __name__ == '__main__':
  main()
