pref("app.update.auto",                     false);
pref("app.update.enabled",                  false);
pref("app.update.autoInstallEnabled",       false);
pref("browser.backspace_action",            2);
pref("browser.display.use_system_colors",   true);
pref("browser.download.folderList",         1);
pref("browser.link.open_external",          3);
pref("browser.shell.checkDefaultBrowser",   false);
pref("general.smoothScroll",                true);
pref("general.useragent.vendor",            "IBM");
pref("general.useragent.vendorSub",         "FIREFOX_RPM_VR");
pref("intl.locale.matchOS",                 true);
pref("storage.nfs_filesystem",              false);
pref("dom.ipc.plugins.enabled.nswrapper*",  false);
pref("network.manage-offline-status",       true);
pref("toolkit.networkmanager.disable",      false);
pref("browser.startup.homepage",            "about:blank");
pref("toolkit.storage.synchronous",         0);
pref("startup.homepage_override_url",       "about:blank");
pref("startup.homepage_welcome_url",        "about:blank");
pref("extensions.shownSelectionUI",         true);
/* Workaround for rhbz#1110291 */
pref("network.negotiate-auth.allow-insecure-ntlm-v1", true);
/* Workaround for mozbz#1063315 */
pref("security.use_mozillapkix_verification", false);
pref("geo.wifi.uri", "https://location.services.mozilla.com/v1/geolocate?key=%MOZILLA_API_KEY%");
pref("browser.tabs.remote.autostart",       false);
