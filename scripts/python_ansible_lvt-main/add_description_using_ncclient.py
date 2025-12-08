# ======================================================================
# Import Modules
# ======================================================================

from ncclient import manager
from ncclient.xml_ import to_ele

# ======================================================================
# Variables
# ======================================================================

DEVICES = [
    {"host": "10.0.0.51",   "port": 830, "username": "admin", "password": "C1sc0123!"},
    {"host": "10.0.0.52",  "port": 830, "username": "admin", "password": "C1sc0123!"},
]
IF_NAME = "GigabitEthernet1"
DESC_TEXT = "Configured via NetConf Ncclient"
# =========================

COMMON_OPTS = {
    "hostkey_verify": False,
    "look_for_keys": False,
    "allow_agent": False,
}

NC_NS = "{urn:ietf:params:xml:ns:netconf:base:1.0}"

EDIT_RPC = f"""
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <edit-config>
    <target><candidate/></target>
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{IF_NAME}</name>
          <description>{DESC_TEXT}</description>
        </interface>
      </interfaces>
    </config>
  </edit-config>
</rpc>
"""

COMMIT_RPC = """
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <commit/>
</rpc>
"""

# ======================================================================
# Build the For Loop
# ======================================================================


for device in DEVICES:
    try:

    except Exception as e:

