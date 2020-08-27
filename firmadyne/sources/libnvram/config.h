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
    PATH("/etc/system_nvram_defaults")

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
    ENTRY("time_zone", nvram_set, "EST5EDT") \
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
    ENTRY("bs_trustedip_enable", nvram_set, "0")

#endif
