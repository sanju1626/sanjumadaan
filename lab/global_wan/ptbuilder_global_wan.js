/**
 * NetArchitect PTBuilder Automation Script: Global WAN Profile (Multi-City Carrier Backbone & Cloud VPC)
 * Generated programmatically from engine data (zero hand-typed addresses).
 * Target Extension: PTBuilder (github.com/kimmknight/PTBuilder)
 * Run in Cisco Packet Tracer: Extensions > Builder Code Editor
 */

function runNetArchitectBuild() {
    // ===========================================================================
    // Phase 1: Add Network Infrastructure Devices on Grid Layout
    // ===========================================================================
    addDevice("R-DEL", "2911", 180, 120);
    addDevice("R-MUM", "2911", 400, 120);
    addDevice("R-BLR", "2911", 620, 120);
    addDevice("R-CHE", "2911", 840, 120);
    addDevice("CLOUD-EDGE", "ISR4331", 1060, 120);

    // ===========================================================================
    // Phase 2: Cable Backbone & Infrastructure Links
    // ===========================================================================
    addLink("R-DEL", "GigabitEthernet0/0", "R-MUM", "GigabitEthernet0/0", "cross"); // OS2 SMF (Carrier DWDM / Transponder) (1150000m)
    addLink("R-DEL", "GigabitEthernet0/1", "R-BLR", "GigabitEthernet0/0", "cross"); // OS2 SMF (Carrier DWDM / Transponder) (1740000m)
    addLink("R-MUM", "GigabitEthernet0/1", "R-BLR", "GigabitEthernet0/1", "cross"); // OS2 SMF (Carrier DWDM / Transponder) (840000m)
    addLink("R-BLR", "GigabitEthernet0/2", "R-CHE", "GigabitEthernet0/0", "cross"); // OS2 SMF (Carrier DWDM / Transponder) (290000m)
    addLink("R-DEL", "GigabitEthernet0/2", "R-CHE", "GigabitEthernet0/1", "cross"); // OS2 SMF (Carrier DWDM / Transponder) (1760000m)
    addLink("R-DEL", "GigabitEthernet0/3", "CLOUD-EDGE", "GigabitEthernet0/0", "cross"); // OS2 SMF (30000m)

    // ===========================================================================
    // Phase 3: Add Test End-Devices (PCs/Servers per Subnet), Static IPs & Cabling
    // ===========================================================================
    addDevice("HOST_DEL_IoT", "PC-PT", 100, 560);
    configurePcIp("HOST_DEL_IoT", false, "10.0.0.2", "255.255.254.0", "10.0.0.1");
    // Note: DEL-IoT (VLAN 10) terminates on a Router-on-a-Stick 802.1Q subinterface on R-DEL; add a 2960 switch to test.
    addDevice("HOST_DEL_Scanners", "PC-PT", 230, 560);
    configurePcIp("HOST_DEL_Scanners", false, "10.0.2.2", "255.255.255.0", "10.0.2.1");
    // Note: DEL-Scanners (VLAN 11) terminates on a Router-on-a-Stick 802.1Q subinterface on R-DEL; add a 2960 switch to test.
    addDevice("HOST_DEL_Corp", "PC-PT", 360, 560);
    configurePcIp("HOST_DEL_Corp", false, "10.0.3.2", "255.255.255.128", "10.0.3.1");
    // Note: DEL-Corp (VLAN 12) terminates on a Router-on-a-Stick 802.1Q subinterface on R-DEL; add a 2960 switch to test.
    addDevice("HOST_MUM_IoT", "PC-PT", 490, 560);
    configurePcIp("HOST_MUM_IoT", false, "10.0.4.2", "255.255.254.0", "10.0.4.1");
    // Note: MUM-IoT (VLAN 20) terminates on a Router-on-a-Stick 802.1Q subinterface on R-MUM; add a 2960 switch to test.
    addDevice("HOST_MUM_Scanners", "PC-PT", 620, 560);
    configurePcIp("HOST_MUM_Scanners", false, "10.0.6.2", "255.255.255.0", "10.0.6.1");
    // Note: MUM-Scanners (VLAN 21) terminates on a Router-on-a-Stick 802.1Q subinterface on R-MUM; add a 2960 switch to test.
    addDevice("HOST_BLR_IoT", "PC-PT", 750, 560);
    configurePcIp("HOST_BLR_IoT", false, "10.0.8.2", "255.255.254.0", "10.0.8.1");
    // Note: BLR-IoT (VLAN 30) terminates on a Router-on-a-Stick 802.1Q subinterface on R-BLR; add a 2960 switch to test.
    addDevice("HOST_BLR_Scanners", "PC-PT", 100, 650);
    configurePcIp("HOST_BLR_Scanners", false, "10.0.10.2", "255.255.255.0", "10.0.10.1");
    // Note: BLR-Scanners (VLAN 31) terminates on a Router-on-a-Stick 802.1Q subinterface on R-BLR; add a 2960 switch to test.
    addDevice("HOST_CHE_IoT", "PC-PT", 230, 650);
    configurePcIp("HOST_CHE_IoT", false, "10.0.12.2", "255.255.254.0", "10.0.12.1");
    // Note: CHE-IoT (VLAN 40) terminates on a Router-on-a-Stick 802.1Q subinterface on R-CHE; add a 2960 switch to test.
    addDevice("HOST_CHE_Scanners", "PC-PT", 360, 650);
    configurePcIp("HOST_CHE_Scanners", false, "10.0.14.2", "255.255.255.0", "10.0.14.1");
    // Note: CHE-Scanners (VLAN 41) terminates on a Router-on-a-Stick 802.1Q subinterface on R-CHE; add a 2960 switch to test.
    addDevice("HOST_Cloud_VPC_Subnet", "Server-PT", 490, 650);
    configurePcIp("HOST_Cloud_VPC_Subnet", false, "10.0.16.2", "255.255.255.0", "10.0.16.1");
    addLink("CLOUD-EDGE", "GigabitEthernet0/2", "HOST_Cloud_VPC_Subnet", "FastEthernet0", "cross");

    // ===========================================================================
    // Phase 4: Push Cisco IOS Configurations (Logical Block-Safe Chunks <= 38 lines)
    // Order: L2 Switches -> L3 Switches -> Routers
    // ===========================================================================
    // --- Configuring R-DEL (2911) ---
    configureIosDevice("R-DEL", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname R-DEL\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\ninterface GigabitEthernet0/0\n description Routed Link to R-MUM [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1150.0 km]\n ip address 10.0.17.1 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1740.0 km]\n ip address 10.0.17.5 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/2\n description Routed Link to R-CHE [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1760.0 km]\n ip address 10.0.17.17 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/3\n description Routed Link to CLOUD-EDGE [Media: OS2 SMF, Distance: 30.0 km]\n ip address 10.0.17.33 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/4\n description Trunk to Local Site LAN Distribution\n no ip address\n no shutdown\ninterface GigabitEthernet0/4.10\n description Subinterface Gateway for DEL-IoT (VLAN 10)\n encapsulation dot1Q 10\n ip address 10.0.0.1 255.255.254.0\n no shutdown\nend");
    configureIosDevice("R-DEL", "enable\nconfigure terminal\ninterface GigabitEthernet0/4.11\n description Subinterface Gateway for DEL-Scanners (VLAN 11)\n encapsulation dot1Q 11\n ip address 10.0.2.1 255.255.255.0\n no shutdown\ninterface GigabitEthernet0/4.12\n description Subinterface Gateway for DEL-Corp (VLAN 12)\n encapsulation dot1Q 12\n ip address 10.0.3.1 255.255.255.128\n no shutdown\ninterface Tunnel0\n description GRE Overlay Span to R-MUM (No-Crypto PT Mode)\n ip address 10.254.0.1 255.255.255.252\n tunnel source GigabitEthernet0/0\n tunnel destination 10.0.17.2\n no shutdown\ninterface Tunnel1\n description GRE Overlay Span to R-BLR (No-Crypto PT Mode)\n ip address 10.254.0.5 255.255.255.252\n tunnel source GigabitEthernet0/1\n tunnel destination 10.0.17.6\n no shutdown\ninterface Tunnel2\n description GRE Overlay Span to R-CHE (No-Crypto PT Mode)\n ip address 10.254.0.9 255.255.255.252\n tunnel source GigabitEthernet0/2\n tunnel destination 10.0.17.18\n no shutdown\nend");
    configureIosDevice("R-DEL", "enable\nconfigure terminal\nrouter ospf 1\n router-id 10.255.255.2\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n no passive-interface GigabitEthernet0/2\n network 10.0.17.0 0.0.0.3 area 0\n network 10.0.17.4 0.0.0.3 area 0\n network 10.0.17.16 0.0.0.3 area 0\n network 10.0.0.0 0.0.1.255 area 0\n network 10.0.2.0 0.0.0.255 area 0\n network 10.0.3.0 0.0.0.127 area 0\n area 1 range 10.0.4.0 255.255.252.0\n area 2 range 10.0.8.0 255.255.252.0\n area 3 range 10.0.12.0 255.255.252.0\nrouter bgp 65001\n bgp router-id 192.168.255.1\n bgp log-neighbor-changes\n neighbor 10.0.17.34 remote-as 65010\n neighbor 10.0.17.34 description eBGP Peering to Cloud VPC\n network 10.0.0.0 mask 255.255.0.0\nip route 10.0.0.0 255.255.0.0 Null0 250\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\nline vty 5 15\n transport input none\nend");

    // --- Configuring R-MUM (2911) ---
    configureIosDevice("R-MUM", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname R-MUM\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\ninterface GigabitEthernet0/0\n description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1150.0 km]\n ip address 10.0.17.2 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 840.0 km]\n ip address 10.0.17.9 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/2\n description Trunk to Local Site LAN Distribution\n no ip address\n no shutdown\ninterface GigabitEthernet0/2.20\n description Subinterface Gateway for MUM-IoT (VLAN 20)\n encapsulation dot1Q 20\n ip address 10.0.4.1 255.255.254.0\n no shutdown\ninterface GigabitEthernet0/2.21\n description Subinterface Gateway for MUM-Scanners (VLAN 21)\n encapsulation dot1Q 21\n ip address 10.0.6.1 255.255.255.0\n no shutdown\nend");
    configureIosDevice("R-MUM", "enable\nconfigure terminal\ninterface Tunnel0\n description GRE Overlay Span to R-DEL (No-Crypto PT Mode)\n ip address 10.254.0.2 255.255.255.252\n tunnel source GigabitEthernet0/0\n tunnel destination 10.0.17.1\n no shutdown\nrouter ospf 1\n router-id 10.255.255.3\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n network 10.0.17.0 0.0.0.3 area 1\n network 10.0.17.8 0.0.0.3 area 1\n network 10.0.4.0 0.0.1.255 area 1\n network 10.0.6.0 0.0.0.255 area 1\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\nline vty 5 15\n transport input none\nend");

    // --- Configuring R-BLR (2911) ---
    configureIosDevice("R-BLR", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname R-BLR\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\ninterface GigabitEthernet0/0\n description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1740.0 km]\n ip address 10.0.17.6 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to R-MUM [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 840.0 km]\n ip address 10.0.17.10 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/2\n description Routed Link to R-CHE [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 290.0 km]\n ip address 10.0.17.13 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/3\n description Trunk to Local Site LAN Distribution\n no ip address\n no shutdown\ninterface GigabitEthernet0/3.30\n description Subinterface Gateway for BLR-IoT (VLAN 30)\n encapsulation dot1Q 30\n ip address 10.0.8.1 255.255.254.0\n no shutdown\nend");
    configureIosDevice("R-BLR", "enable\nconfigure terminal\ninterface GigabitEthernet0/3.31\n description Subinterface Gateway for BLR-Scanners (VLAN 31)\n encapsulation dot1Q 31\n ip address 10.0.10.1 255.255.255.0\n no shutdown\ninterface Tunnel0\n description GRE Overlay Span to R-DEL (No-Crypto PT Mode)\n ip address 10.254.0.6 255.255.255.252\n tunnel source GigabitEthernet0/0\n tunnel destination 10.0.17.5\n no shutdown\nrouter ospf 1\n router-id 10.255.255.4\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n no passive-interface GigabitEthernet0/2\n network 10.0.17.4 0.0.0.3 area 2\n network 10.0.17.8 0.0.0.3 area 2\n network 10.0.17.12 0.0.0.3 area 2\n network 10.0.8.0 0.0.1.255 area 2\n network 10.0.10.0 0.0.0.255 area 2\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\nline vty 5 15\n transport input none\nend");

    // --- Configuring R-CHE (2911) ---
    configureIosDevice("R-CHE", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname R-CHE\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\ninterface GigabitEthernet0/0\n description Routed Link to R-BLR [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 290.0 km]\n ip address 10.0.17.14 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to R-DEL [Media: OS2 SMF (Carrier DWDM / Transponder), Distance: 1760.0 km]\n ip address 10.0.17.18 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/2\n description Trunk to Local Site LAN Distribution\n no ip address\n no shutdown\ninterface GigabitEthernet0/2.40\n description Subinterface Gateway for CHE-IoT (VLAN 40)\n encapsulation dot1Q 40\n ip address 10.0.12.1 255.255.254.0\n no shutdown\ninterface GigabitEthernet0/2.41\n description Subinterface Gateway for CHE-Scanners (VLAN 41)\n encapsulation dot1Q 41\n ip address 10.0.14.1 255.255.255.0\n no shutdown\nend");
    configureIosDevice("R-CHE", "enable\nconfigure terminal\ninterface Tunnel0\n description GRE Overlay Span to R-DEL (No-Crypto PT Mode)\n ip address 10.254.0.10 255.255.255.252\n tunnel source GigabitEthernet0/1\n tunnel destination 10.0.17.17\n no shutdown\nrouter ospf 1\n router-id 10.255.255.5\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n network 10.0.17.12 0.0.0.3 area 3\n network 10.0.17.16 0.0.0.3 area 3\n network 10.0.12.0 0.0.1.255 area 3\n network 10.0.14.0 0.0.0.255 area 3\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\nline vty 5 15\n transport input none\nend");

    // --- Configuring CLOUD-EDGE (ISR4331) ---
    configureIosDevice("CLOUD-EDGE", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname CLOUD-EDGE\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\ninterface GigabitEthernet0/0\n description Routed Link to R-DEL [Media: OS2 SMF, Distance: 30.0 km]\n ip address 10.0.17.34 255.255.255.252\n no shutdown\ninterface GigabitEthernet0/2\n description Local LAN Gateway for Cloud-VPC-Subnet\n ip address 10.0.16.1 255.255.255.0\n no shutdown\nrouter bgp 65010\n bgp router-id 192.168.255.5\n bgp log-neighbor-changes\n neighbor 10.0.17.33 remote-as 65001\n neighbor 10.0.17.33 description eBGP Peering to Enterprise Delhi Hub\n network 10.0.16.0 mask 255.255.255.0\nip route 10.0.16.0 255.255.255.0 Null0 250\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\nend");
    configureIosDevice("CLOUD-EDGE", "enable\nconfigure terminal\nline vty 5 15\n transport input none\nend");

}

runNetArchitectBuild();
