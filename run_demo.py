import os
import sys
import shlex
import subprocess
import argparse
import time
from shutil import copyfile, copytree, rmtree

NO_PROMPT = False

def prompt_key(prompt):
  if NO_PROMPT:
    print("\n" + prompt)
    return
  inp = False
  while inp != "":
    try:
      inp = input("\n{} -- press any key to continue".format(prompt))
    except Exception:
      pass

def supply_chain():

  prompt_key("Define supply chain layout (Alice)")
  os.chdir("owner_martin")
  create_layout_cmd = "python create_layout.py"
  print(create_layout_cmd)
  subprocess.call(shlex.split(create_layout_cmd))

  prompt_key("Clone source code (Bob)")
  os.chdir("../functionary_jaja")
  clone_cmd = ("in-toto-run"
                    " --verbose"
                    " --use-dsse"
                    " --step-name clone --products demo-reference-for-in-toto/security-guild-rocks.py"
                    " --signing-key jaja -- git clone https://github.com/in-toto/demo-reference-for-in-toto.git")
  print(clone_cmd)
  subprocess.call(shlex.split(clone_cmd))

  prompt_key("Update version number (Bob)")
  update_version_start_cmd = ("in-toto-record"
                    " start"
                    " --verbose"
                    " --use-dsse"
                    " --step-name update-version"
                    " --signing-key jaja"
                    " --materials demo-reference-for-in-toto/security-guild-rocks.py")

  print(update_version_start_cmd)
  subprocess.call(shlex.split(update_version_start_cmd))

  update_version = "echo 'VERSION = \"foo-v1\"\n\nprint(\"Hello in-toto\")\n' > demo-reference-for-in-toto/security-guild-rocks.py"
  print(update_version)
  subprocess.call(update_version, shell=True)

  update_version_stop_cmd = ("in-toto-record"
                    " stop"
                    " --verbose"
                    " --use-dsse"
                    " --step-name update-version"
                    " --signing-key jaja"
                    " --products demo-reference-for-in-toto/security-guild-rocks.py")

  print(update_version_stop_cmd)
  subprocess.call(shlex.split(update_version_stop_cmd))

  copytree("demo-reference-for-in-toto", "../functionary_manu/demo-reference-for-in-toto")

  prompt_key("Package (Carl)")
  os.chdir("../functionary_manu")
  package_cmd = ("in-toto-run"
                 " --verbose"
                 " --use-dsse"
                 " --step-name package --materials demo-reference-for-in-toto/security-guild-rocks.py"
                 " --products demo-reference-for-in-toto.tar.gz"
                 " --signing-key manu --record-streams"
                 " -- tar --exclude '.git' -zcvf demo-reference-for-in-toto.tar.gz demo-reference-for-in-toto")
  print(package_cmd)
  subprocess.call(shlex.split(package_cmd))


  prompt_key("Create final product")
  os.chdir("..")
  copyfile("owner_martin/root.layout", "final_product/root.layout")
  copyfile("functionary_jaja/clone.210dcc50.link", "final_product/clone.210dcc50.link")
  copyfile("functionary_jaja/update-version.210dcc50.link", "final_product/update-version.210dcc50.link")
  copyfile("functionary_manu/package.be06db20.link", "final_product/package.be06db20.link")
  copyfile("functionary_manu/demo-reference-for-in-toto.tar.gz", "final_product/demo-reference-for-in-toto.tar.gz")


  prompt_key("Verify final product (client)")
  os.chdir("final_product")
  copyfile("../owner_martin/martin.pub", "martin.pub")
  verify_cmd = ("in-toto-verify"
                " --verbose"
                " --layout root.layout"
                " --verification-keys martin.pub")
  print(verify_cmd)
  retval = subprocess.call(shlex.split(verify_cmd))
  print("Return value: " + str(retval))




  prompt_key("Tampering with the supply chain")
  os.chdir("../functionary_manu")
  tamper_cmd = "echo 'something evil' >> demo-reference-for-in-toto/security-guild-rocks.py"
  print(tamper_cmd)
  subprocess.call(tamper_cmd, shell=True)


  prompt_key("Package (Carl)")
  package_cmd = ("in-toto-run"
                 " --verbose"
                 " --use-dsse"
                 " --step-name package --materials demo-reference-for-in-toto/security-guild-rocks.py"
                 " --products demo-reference-for-in-toto.tar.gz"
                 " --signing-key manu --record-streams"
                 " -- tar --exclude '.git' -zcvf demo-reference-for-in-toto.tar.gz demo-reference-for-in-toto")
  print(package_cmd)
  subprocess.call(shlex.split(package_cmd))


  prompt_key("Create final product")
  os.chdir("..")
  copyfile("owner_martin/root.layout", "final_product/root.layout")
  copyfile("functionary_jaja/clone.210dcc50.link", "final_product/clone.210dcc50.link")
  copyfile("functionary_jaja/update-version.210dcc50.link", "final_product/update-version.210dcc50.link")
  copyfile("functionary_manu/package.be06db20.link", "final_product/package.be06db20.link")
  copyfile("functionary_manu/demo-reference-for-in-toto.tar.gz", "final_product/demo-reference-for-in-toto.tar.gz")


  prompt_key("Verify final product (client)")
  os.chdir("final_product")
  copyfile("../owner_martin/martin.pub", "martin.pub")
  verify_cmd = ("in-toto-verify"
                " --verbose"
                " --layout root.layout"
                " --verification-keys martin.pub")

  print(verify_cmd)
  retval = subprocess.call(shlex.split(verify_cmd))
  print("Return value: " + str(retval))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--no-prompt", help="No prompt.",
      action="store_true")
  parser.add_argument("-c", "--clean", help="Remove files created during demo.",
      action="store_true")
  args = parser.parse_args()

  if args.clean:
    files_to_delete = [
      "owner_martin/root.layout",
      "functionary_jaja/clone.210dcc50.link",
      "functionary_jaja/update-version.210dcc50.link",
      "functionary_jaja/demo-reference-for-in-toto",
      "functionary_manu/package.be06db20.link",
      "functionary_manu/demo-reference-for-in-toto.tar.gz",
      "functionary_manu/demo-reference-for-in-toto",
      "final_product/martin.pub",
      "final_product/demo-reference-for-in-toto.tar.gz",
      "final_product/package.be06db20.link",
      "final_product/clone.210dcc50.link",
      "final_product/update-version.210dcc50.link",
      "final_product/untar.link",
      "final_product/root.layout",
      "final_product/demo-reference-for-in-toto",
    ]

    for path in files_to_delete:
      if os.path.isfile(path):
        os.remove(path)
      elif os.path.isdir(path):
        rmtree(path)

    sys.exit(0)
  if args.no_prompt:
    global NO_PROMPT
    NO_PROMPT = True


  supply_chain()

if __name__ == '__main__':
  main()
