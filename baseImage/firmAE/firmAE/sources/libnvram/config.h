#ifndef INCLUDE_CONFIG_H
#define INCLUDE_CONFIG_H

// Determines whether debugging information should be printed to stderr.
#define DEBUG               1
// Determines the size of the internal buffer, used for manipulating and storing key values, etc.
#define BUFFER_SIZE         256
// Determines the size of the "emulated" NVRAM, used by nvram_get_nvramspace().
#define NVRAM_SIZE          2048
// Determines the maximum size of the user-supplied output buffer when a length is not supplied.
#define USER_BUFFER_SIZE    64
// Determines the unique separator character (as string) used for the list implementation. Do not use "\0".
#define LIST_SEP            "\xff"
// Special argument used to change the semantics of the nvram_list_exist() function.
#define LIST_MAGIC          0xdeadbeef
// Identifier value used to generate IPC key in ftok()
#define IPC_KEY             'A'
// Timeout for the semaphore
#define IPC_TIMEOUT         1000
// Mount point of the base NVRAM implementation.
#define MOUNT_POINT         "/firmadyne/libnvram/"
// Location of NVRAM override values that are copied into the base NVRAM implementation.
#define OVERRIDE_POINT      "/firmadyne/libnvram.override/"

// Define the semantics for success and failure error codes.
#define E_FAILURE  0
#define E_SUCCESS  1

// Default paths for NVRAM default values.
#define NVRAM_DEFAULTS_PATH \
    /* "DIR-505L_FIRMWARE_1.01.ZIP" (10497) */ \
    PATH("/var/etc/nvram.default") \
    /* "DIR-615_REVE_FIRMWARE_5.11.ZIP" (9753) */ \
    PATH("/etc/nvram.default") \
    /* "DGL-5500_REVA_FIRMWARE_1.12B05.ZIP" (9469) */ \
    TABLE(router_defaults) \
    PATH("/etc/nvram.conf") \
    PATH("/etc/nvram.deft") \
    PATH("/etc/nvram.update") \
    TABLE(Nvrams) \
    PATH("/etc/wlan/nvram_params") \
    PATH("/etc/system_nvram_defaults") \
    FIRMAE_PATH("/image/mnt/nvram_ap.default") \
    /* "DCS-931L_FIRMWARE_1.04B1.ZIP" by SR */\
    FIRMAE_PATH("/etc_ro/Wireless/RT2860AP/RT2860_default_vlan") \
    FIRMAE_PATH("/etc_ro/Wireless/RT2860AP/RT2860_default_novlan") \
    /* "DGN3500-V1.1.00.30_NA.zip" */\
    FIRMAE_PATH2("/usr/etc/default") \
    /* "JR6150-R6050-V1.0.0.22.zip" by SR */ \
    FIRMAE_PATH("/image/mnt/nvram_whp.default") \
    FIRMAE_PATH("/image/mnt/nvram_rt.default") \
    FIRMAE_PATH("/image/mnt/nvram_rpt.default") \
    FIRMAE_PATH("/image/mnt/nvram.default")

// Default values for NVRAM.
#define NVRAM_DEFAULTS \
    /* Linux kernel log level, used by "WRT54G3G_2.11.05_ETSI_code.bin" (305) */ \
    ENTRY("console_loglevel", nvram_set, "7") \
    /* Reset NVRAM to default at bootup, used by "WNR3500v2-V1.0.2.10_23.0.70NA.chk" (1018) */ \
    ENTRY("restore_defaults", nvram_set, "1") \
    ENTRY("sku_name", nvram_set, "") \
    ENTRY("wla_wlanstate", nvram_set, "") \
    ENTRY("lan_if", nvram_set, "br0") \
    ENTRY("lan_ipaddr", nvram_set, "192.168.0.50") \
    ENTRY("lan_bipaddr", nvram_set, "192.168.0.255") \
    ENTRY("lan_netmask", nvram_set, "255.255.255.0") \
    /* Set default timezone, required by multiple images */ \
    ENTRY("time_zone", nvram_set, "PST8PDT") \
    /* Set default WAN MAC address, used by "NBG-416N_V1.00(USA.7)C0.zip" (12786) */ \
    ENTRY("wan_hwaddr_def", nvram_set, "01:23:45:67:89:ab") \
    /* Attempt to define LAN/WAN interfaces */ \
    ENTRY("wan_ifname", nvram_set, "eth0") \
    ENTRY("lan_ifnames", nvram_set, "eth1 eth2 eth3 eth4") \
    /* Used by "TEW-638v2%201.1.5.zip" (12898) to prevent crash in 'goahead' */ \
    ENTRY("ethConver", nvram_set, "1") \
    /* Used by "Firmware_TEW-411BRPplus_2.07_EU.zip" (13649) to prevent crash in 'init' */ \
    ENTRY("lan_proto", nvram_set, "dhcp") \
    ENTRY("wan_ipaddr", nvram_set, "0.0.0.0") \
    ENTRY("wan_netmask", nvram_set, "255.255.255.0") \
    ENTRY("wanif", nvram_set, "eth0") \
    /* Used by "DGND3700 Firmware Version 1.0.0.17(NA).zip" (3425) to prevent crashes */ \
    ENTRY("time_zone_x", nvram_set, "0") \
    ENTRY("rip_multicast", nvram_set, "0") \
    ENTRY("bs_trustedip_enable", nvram_set, "0") \
    /* Set default MAC address, used by "linux-lzma(550A)" by SR */ \
    FIRMAE_ENTRY("et0macaddr", nvram_set, "01:23:45:67:89:ab")\
    /* Used by "AC1450-V1.0.0.34_10.0.16.zip" to prevent crashes by SR */ \
    FIRMAE_ENTRY("filter_rule_tbl", nvram_set, "") \
    /* Used by Netgear "R6200V2-V1.0.1.14_1.0.14.zip" by SR */ \
    FIRMAE_ENTRY("pppoe2_schedule_config", nvram_set, "127:0:0:23:59") \
    FIRMAE_ENTRY("schedule_config", nvram_set, "127:0:0:23:59") \
    /* Used by Netgear WNDR3400v3, WNDR3500v3 "WNR3500L-V1.2.0.18_40.0.67" to prevent crashes due to following "atoi" func by SR */ \
    FIRMAE_ENTRY("access_control_mode", nvram_set, "0") \
    FIRMAE_ENTRY("fwpt_df_count", nvram_set, "0") \
    FIRMAE_ENTRY("static_if_status", nvram_set, "1") \
    /* R8500 patch to prevent crashes in httpd */ \
    FIRMAE_ENTRY("www_relocation", nvram_set, "") \
    FIRMAE_FOR_ENTRY("usb_info_dev%d", nvram_set, "A200396E0402FF83@1@14.4G@U@1@USB_Storage;U:;0;0@", 0, 101) \
    /* R6200V2, R6250-V1, R6300v2, R6400, R6700-V1, R7000-V1, R7900, R8000, R8500 patch to prevent crashes in httpd */ \
    FIRMAE_FOR_ENTRY("wla_ap_isolate_%d", nvram_set, "", 1, 5) \
    /* R6200V1 patch to prevent crashes in httpd */ \
    FIRMAE_FOR_ENTRY("wlg_ap_isolate_%d", nvram_set, "", 1, 5) \
    FIRMAE_FOR_ENTRY("wlg_allow_access_%d", nvram_set, "", 1, 5) \
    /* R6400-V1, R7900-V1, R8000, R8500 patch to prevent crashes in httpd */ \
    FIRMAE_FOR_ENTRY("%d:macaddr", nvram_set, "01:23:45:67:89:ab", 0, 3) \
    FIRMAE_FOR_ENTRY("lan%d_ifnames", nvram_set, "", 1, 10)

#endif
