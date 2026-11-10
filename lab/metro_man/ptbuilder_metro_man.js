/**
 * NetArchitect PTBuilder Automation Script: Metro MAN Profile (Tri-Site Metropolitan Ring)
 * Generated programmatically from engine data (zero hand-typed addresses).
 * Target Extension: PTBuilder (github.com/kimmknight/PTBuilder)
 * Run in Cisco Packet Tracer: Extensions > Builder Code Editor
 */

function runNetArchitectBuild() {
    // ===========================================================================
    // Phase 1: Add Network Infrastructure Devices on Grid Layout
    // ===========================================================================
    addDevice("HQ-CORE", "3650-24PS", 400, 260);
    addDevice("REM1-R", "2911", 180, 120);
    addDevice("REM2-R", "2911", 400, 120);

    // ===========================================================================
    // Phase 2: Cable Backbone & Infrastructure Links
    // ===========================================================================
    addLink("HQ-CORE", "GigabitEthernet1/0/1", "REM1-R", "GigabitEthernet0/0", "straight"); // OS2 SMF (15000m)
    addLink("HQ-CORE", "GigabitEthernet1/0/2", "REM2-R", "GigabitEthernet0/0", "straight"); // OS2 SMF (35000m)
    addLink("REM1-R", "GigabitEthernet0/1", "REM2-R", "GigabitEthernet0/1", "cross"); // OS2 SMF (22000m)

    // ===========================================================================
    // Phase 3: Add Test End-Devices (PCs/Servers per Subnet), Static IPs & Cabling
    // ===========================================================================
    addDevice("HOST_HQ_Users", "PC-PT", 100, 560);
    configurePcIp("HOST_HQ_Users", false, "172.16.0.2", "255.255.254.0", "172.16.0.1");
    addLink("HQ-CORE", "GigabitEthernet1/0/3", "HOST_HQ_Users", "FastEthernet0", "straight");
    addDevice("HOST_REM1_Users", "PC-PT", 230, 560);
    configurePcIp("HOST_REM1_Users", false, "172.16.2.2", "255.255.255.128", "172.16.2.1");
    addLink("REM1-R", "GigabitEthernet0/2", "HOST_REM1_Users", "FastEthernet0", "cross");
    addDevice("HOST_REM2_Users", "PC-PT", 360, 560);
    configurePcIp("HOST_REM2_Users", false, "172.16.2.130", "255.255.255.128", "172.16.2.129");
    addLink("REM2-R", "GigabitEthernet0/2", "HOST_REM2_Users", "FastEthernet0", "cross");
    addDevice("HOST_HQ_Servers", "Server-PT", 490, 560);
    configurePcIp("HOST_HQ_Servers", false, "172.16.3.2", "255.255.255.192", "172.16.3.1");
    addLink("HQ-CORE", "GigabitEthernet1/0/4", "HOST_HQ_Servers", "FastEthernet0", "straight");
    addDevice("HOST_FinTech_Colo", "Server-PT", 620, 560);
    configurePcIp("HOST_FinTech_Colo", false, "172.16.3.66", "255.255.255.192", "172.16.3.65");
    addLink("HQ-CORE", "GigabitEthernet1/0/5", "HOST_FinTech_Colo", "FastEthernet0", "straight");
    addDevice("HOST_HQ_Mgmt", "PC-PT", 750, 560);
    configurePcIp("HOST_HQ_Mgmt", false, "172.16.3.130", "255.255.255.224", "172.16.3.129");
    addLink("HQ-CORE", "GigabitEthernet1/0/6", "HOST_HQ_Mgmt", "FastEthernet0", "straight");

    // ===========================================================================
    // Phase 4: Push Cisco IOS Configurations (Logical Block-Safe Chunks <= 38 lines)
    // Order: L2 Switches -> L3 Switches -> Routers
    // ===========================================================================
    // --- Configuring HQ-CORE (3650-24PS) ---
    configureIosDevice("HQ-CORE", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname HQ-CORE\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip routing\nip cef\nspanning-tree mode rapid-pvst\nspanning-tree extend system-id\nspanning-tree vlan 1-4094 priority 4096\nclass-map match-any CM_VOIP_FINTECH\n match ip dscp ef\n match ip dscp cs5\npolicy-map PM_METRO_QOS_EGRESS\n class CM_VOIP_FINTECH\n priority percent 35\n class class-default\n fair-queue\nvlan 10\n name HQ-Users\nvlan 100\n name HQ-Servers\nvlan 150\n name FinTech-Colo\nvlan 99\n name HQ-Mgmt\nvlan 999\n name Parking_Native_Blackhole\nend");
    configureIosDevice("HQ-CORE", "enable\nconfigure terminal\ninterface GigabitEthernet1/0/1\n description Routed Point-to-Point Uplink to REM1-R [Media: OS2 SMF, Distance: 15.0 km]\n no switchport\n ip address 172.16.3.161 255.255.255.252\n ip ospf cost 10\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet1/0/2\n description Routed Point-to-Point Uplink to REM2-R [Media: OS2 SMF, Distance: 35.0 km]\n no switchport\n ip address 172.16.3.165 255.255.255.252\n ip ospf cost 20\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet1/0/3\n description Local Access Port for HQ-Users (VLAN 10)\n switchport mode access\n switchport access vlan 10\n spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\ninterface GigabitEthernet1/0/4\n description Local Access Port for HQ-Servers (VLAN 100)\n switchport mode access\n switchport access vlan 100\n spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\ninterface GigabitEthernet1/0/5\n description Local Access Port for FinTech-Colo (VLAN 150)\n switchport mode access\n switchport access vlan 150\n spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\nend");
    configureIosDevice("HQ-CORE", "enable\nconfigure terminal\ninterface GigabitEthernet1/0/6\n description Local Access Port for HQ-Mgmt (VLAN 99)\n switchport mode access\n switchport access vlan 99\n spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\ninterface Vlan10\n description SVI Default Gateway for HQ-Users\n ip address 172.16.0.1 255.255.254.0\n no shutdown\ninterface Vlan100\n description SVI Default Gateway for HQ-Servers\n ip address 172.16.3.1 255.255.255.192\n no shutdown\ninterface Vlan150\n description SVI Default Gateway for FinTech-Colo\n ip address 172.16.3.65 255.255.255.192\n no shutdown\ninterface Vlan99\n description SVI Default Gateway for HQ-Mgmt\n ip address 172.16.3.129 255.255.255.224\n no shutdown\nrouter ospf 1\n router-id 10.255.255.1\n passive-interface default\n no passive-interface GigabitEthernet1/0/1\n no passive-interface GigabitEthernet1/0/2\n network 172.16.0.0 0.0.1.255 area 0\n network 172.16.3.0 0.0.0.63 area 0\n network 172.16.3.64 0.0.0.63 area 0\n network 172.16.3.128 0.0.0.31 area 0\n network 172.16.3.160 0.0.0.3 area 0\n network 172.16.3.164 0.0.0.3 area 0\nend");
    configureIosDevice("HQ-CORE", "enable\nconfigure terminal\nip access-list standard ACL_MGMT_VTY\n permit 172.16.3.128 0.0.0.31\n deny any log\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\n access-class ACL_MGMT_VTY in\nline vty 5 15\n transport input none\nend");

    // --- Configuring REM1-R (2911) ---
    configureIosDevice("REM1-R", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname REM1-R\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\nclass-map match-any CM_VOIP_FINTECH\n match ip dscp ef\n match ip dscp cs5\npolicy-map PM_METRO_QOS_EGRESS\n class CM_VOIP_FINTECH\n priority percent 35\n class class-default\n fair-queue\ninterface GigabitEthernet0/0\n description Routed Link to HQ-CORE [Media: OS2 SMF, Distance: 15.0 km]\n ip address 172.16.3.162 255.255.255.252\n ip ospf cost 10\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to REM2-R [Media: OS2 SMF, Distance: 22.0 km]\n ip address 172.16.3.169 255.255.255.252\n ip ospf cost 100\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet0/2\n description Local LAN Gateway for REM1-Users (VLAN 20 Untagged Access)\n ip address 172.16.2.1 255.255.255.128\n no shutdown\nend");
    configureIosDevice("REM1-R", "enable\nconfigure terminal\nrouter ospf 1\n router-id 10.255.255.2\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n network 172.16.3.160 0.0.0.3 area 0\n network 172.16.3.168 0.0.0.3 area 0\n network 172.16.2.0 0.0.0.127 area 0\nip access-list standard ACL_MGMT_VTY\n permit 172.16.3.128 0.0.0.31\n deny any log\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\n access-class ACL_MGMT_VTY in\nline vty 5 15\n transport input none\nend");

    // --- Configuring REM2-R (2911) ---
    configureIosDevice("REM2-R", "enable\nconfigure terminal\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nservice password-encryption\nhostname REM2-R\nno ip domain-lookup\nip domain-name netarchitect.lab\nusername admin privilege 15 secret CHANGE_ME\nenable secret CHANGE_ME\nip ssh version 2\nip cef\nclass-map match-any CM_VOIP_FINTECH\n match ip dscp ef\n match ip dscp cs5\npolicy-map PM_METRO_QOS_EGRESS\n class CM_VOIP_FINTECH\n priority percent 35\n class class-default\n fair-queue\ninterface GigabitEthernet0/0\n description Routed Link to HQ-CORE [Media: OS2 SMF, Distance: 35.0 km]\n ip address 172.16.3.166 255.255.255.252\n ip ospf cost 20\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet0/1\n description Routed Link to REM1-R [Media: OS2 SMF, Distance: 22.0 km]\n ip address 172.16.3.170 255.255.255.252\n ip ospf cost 100\n service-policy output PM_METRO_QOS_EGRESS\n no shutdown\ninterface GigabitEthernet0/2\n description Local LAN Gateway for REM2-Users (VLAN 30 Untagged Access)\n ip address 172.16.2.129 255.255.255.128\n no shutdown\nend");
    configureIosDevice("REM2-R", "enable\nconfigure terminal\nrouter ospf 1\n router-id 10.255.255.3\n passive-interface default\n no passive-interface GigabitEthernet0/0\n no passive-interface GigabitEthernet0/1\n network 172.16.3.164 0.0.0.3 area 0\n network 172.16.3.168 0.0.0.3 area 0\n network 172.16.2.128 0.0.0.127 area 0\nip access-list standard ACL_MGMT_VTY\n permit 172.16.3.128 0.0.0.31\n deny any log\nline con 0\n exec-timeout 10 0\n logging synchronous\n login local\nline aux 0\nline vty 0 4\n exec-timeout 10 0\n logging synchronous\n login local\n transport input ssh\n access-class ACL_MGMT_VTY in\nline vty 5 15\n transport input none\nend");

}

runNetArchitectBuild();
