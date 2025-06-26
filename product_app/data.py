registry_url = "registry.opentext.com"
artifactory_url = "artifactory.otxlab.net"
ot2paas = "ot2-paas"

PATCH_DATA = {
        "24.2": {
            "Server": {
                "ot-dctm-server": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-server"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-server"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-server"},
                }
            },
            "IJMS": {
                "ot-dctm-ijms": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-ijms"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-ijms"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-ijms"},
                }
            },
            "DFS": {
                "ot-dctm-dfs": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-dfs"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-dfs"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-dfs"},
                }
            },
            "CMIS": {
                "ot-dctm-cmis": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-cmis"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-cmis"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-cmis"},
                }
            },
            "Documentum ReST": {
                "ot-dctm-rest": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-rest"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-rest"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-rest"},
                }
            },
            "Common": {
                "dctm-tomcat": {
                    "registry": {"registry": registry_url, "path": "common", "image_name": "alpinelinux-openjdk-tomcat"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "dctm-tomcat"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "dctm-tomcat"},
                }
            },
            "D2": {
                "ot-dctm-d2cp-installer": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2cp-installer"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2cp-installer"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2cp-installer"},
                },
                "ot-dctm-d2pp-installer": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2pp-installer"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2pp-installer"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2pp-installer"},
                },
                "ot-dctm-d2cp-ijms": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2cp-ijms"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2cp-ijms"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2cp-ijms"},
                },
                "ot-dctm-d2pp-ijms": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2pp-ijms"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2pp-ijms"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2pp-ijms"},
                },
                "ot-dctm-d2cp-rest": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2cp-rest"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2cp-rest"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2cp-rest"},
                },
                "ot-dctm-d2pp-rest": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2pp-rest"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2pp-rest"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2pp-rest"},
                },
                "ot-dctm-d2cp-smartview": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2cp-smartview"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2cp-smartview"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2cp-smartview"},
                },
                "ot-dctm-d2pp-smartview": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2pp-smartview"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2pp-smartview"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2pp-smartview"},
                },
                "ot-dctm-d2cp-config": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2cp-config"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2cp-config"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2cp-config"},
                },
                "ot-dctm-d2pp-config": {
                    "registry": {"registry": registry_url, "path": "", "image_name": "ot-dctm-d2pp-config"},
                    "ot2paas": {"registry": artifactory_url, "path": "ot2paas", "image_name": "ot-dctm-d2pp-config"},
                    "local": {"registry": artifactory_url, "path": "bpdockerhub", "image_name": "ot-dctm-d2pp-config"},
                },
            },
        },
        "24.4": {
            "Server": {
                "ot-dctm-server": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-server",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-server",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-server",
                    },
                },
            },
            "IJMS": {
                "ot-dctm-ijms": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-ijms",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-ijms",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-ijms",
                    },
                },
            },
            "DFS": {
                "ot-dctm-dfs": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-dfs",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-dfs",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-dfs",
                    },
                },
            },
            "CMIS": {
                "ot-dctm-cmis": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-cmis",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-cmis",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-cmis",
                    },
                },
            },
            "DA": {
                "ot-dctm-admin": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-admin",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-admin",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-admin",
                    },
                },
            },
            "Records": {
                "ot-dctm-records": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-records",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-records",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-records",
                    },
                },
                "ot-dctm-records-darinstallation": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-records-darinstallation",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-records-darinstallation",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-records-darinstallation",
                    },
                },
                "ot-dctm-rqm": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-rqm",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-rqm",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-rqm",
                    },
                },
            },
            "Documentum ReST": {
                "ot-dctm-restart": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-restart",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-restart",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-restart",
                    },
                },
                "ot-dctm-rest": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-rest",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-rest",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-rest",
                    },
                },
                "ot-dctm-tomcat": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-tomcat",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-tomcat",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-tomcat",
                    },
                },
            },
            "Common": {
                "common/alpinelinux-openjdk-tomcat:dctm-alpinelinux3-temurinopenjdk17.0.14-tomcat10.1.36": {
                    "registry": {
                        "registry": registry_url,
                        "path": "common",
                        "image_name": "alpinelinux-openjdk-tomcat:dctm-alpinelinux3-temurinopenjdk17.0.14-tomcat10.1.36",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": f"{ot2paas}/common",
                        "image_name": "alpinelinux-openjdk-tomcat:dctm-alpinelinux3-temurinopenjdk17.0.14-tomcat10.1.36",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub/common",
                        "image_name": "alpinelinux-openjdk-tomcat:dctm-alpinelinux3-temurinopenjdk17.0.14-tomcat10.1.36",
                    },
                },
            },
            "D2": {
                "ot-dctm-client-installer": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-installer",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-installer",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-installer",
                    },
                },
                "ot-dctm-client-config": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-config",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-config",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-config",
                    },
                },
                "ot-dctm-client-classic": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-classic",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-classic",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-classic",
                    },
                },
                "ot-dctm-client-rest": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-rest",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-rest",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-rest",
                    },
                },
                "ot-dctm-client-smartview": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-smartview",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-smartview",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-smartview",
                    },
                },
                "ot-dctm-client-ijms": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-ijms",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-ijms",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-ijms",
                    },
                },
                "ot-dctm-client-mobile": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-client-mobile",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-client-mobile",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-client-mobile",
                    },
                },
            },
            "Workflow Designer": {
                "ot-dctm-bpm-installer": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-bpm-installer",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-bpm-installer",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-bpm-installer",
                    },
                },
                "ot-dctm-workflow-designer": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-workflow-designer",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-workflow-designer",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-workflow-designer",
                    },
                },
            },
            "Advanced Workflow": {
                "ot-dctm-bps": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-bps",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-bps",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-bps",
                    },
                },
                "ot-dctm-xda": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-xda",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-xda",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-xda",
                    },
                },
                "ot-dctm-xda-tools": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-xda-tools",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-xda-tools",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-xda-tools",
                    },
                },
            },
            "XECM": {
                "ot-dctm-smartviewm365-ns": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-smartviewm365-ns",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-smartviewm365-ns",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-smartviewm365-ns",
                    },
                },
                "ot-dctm-smartviewm365customjar": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "smartviewm365customjar",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "smartviewm365customjar",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "smartviewm365customjar",
                    },
                },
                "ot-dctm-smartviewm365": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-smartviewm365",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-smartviewm365",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-smartviewm365",
                    },
                },
            },
            "Content Connect": {
                "ot-dctm-content-connect-dbinit": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-content-connect-dbinit",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-content-connect-dbinit",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-content-connect-dbinit",
                    },
                },
                "ot-dctm-content-connect": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-content-connect",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-content-connect",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-content-connect",
                    },
                },
            },
            "SAP Connectors": {
                "ot-dctm-assap": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-assap",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-assap",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-sapc-docker-rel",
                        "image_name": "ot-dctm-assap",
                    },
                },
                "ot-dctm-admin-sapconnector": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-admin-sapconnector",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-admin-sapconnector",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-sapc-docker-rel",
                        "image_name": "ot-dctm-admin-sapconnector",
                    },
                },
                "ot-dctm-cssap": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-cssap",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-cssap",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-sapc-docker-rel",
                        "image_name": "ot-dctm-cssap",
                    },
                },
                "ot-dctm-assap-ilm": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-assap-ilm",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-assap-ilm",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-sapc-docker-rel",
                        "image_name": "ot-dctm-assap-ilm",
                    },
                },
            },
            "Documentum Search": {
                "ot-dctm-search-admin": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-search-admin",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-search-admin",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-search-admin",
                    },
                },
                "ot-dctm-index-agent": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-index-agent",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-index-agent",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-index-agent",
                    },
                },
                "ot-dctm-search-parser": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-search-parser",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-search-parser",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-search-parser",
                    },
                },
                "ot-dctm-search-agent": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-search-agent",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-search-agent",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-search-agent",
                    },
                },
                "ot-dctm-zk-status-checker": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-zk-status-checker",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-zk-status-checker",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-zk-status-checker",
                    },
                },
                "ot-dctm-content-fetcher": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-content-fetcher",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-content-fetcher",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-content-fetcher",
                    },
                },
                "ot-coresearch-api": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-coresearch-api",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-coresearch-api",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-coresearch-api",
                    },
                },
                "ot-dctm-solr": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-solr",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-solr",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-solr",
                    },
                },
                "ot-coresearch-indexer": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-coresearch-indexer",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-coresearch-indexer",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "bpdockerhub",
                        "image_name": "ot-coresearch-indexer",
                    },
                },
            },
            "DTR": {
                "ot-dctm-reports-base": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-reports-base",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-reports-base",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-reports-base",
                    },
                },
                "ot-dctm-reports-d2": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-reports-d2",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-reports-d2",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-reports-d2",
                    },
                },
                "ot-dctm-reports-installer": {
                    "registry": {
                        "registry": registry_url,
                        "path": "",
                        "image_name": "ot-dctm-reports-installer",
                    },
                    "ot2paas": {
                        "registry": artifactory_url,
                        "path": ot2paas,
                        "image_name": "ot-dctm-reports-installer",
                    },
                    "local": {
                        "registry": artifactory_url,
                        "path": "cs-dctmclient-docker-rel-local",
                        "image_name": "ot-dctm-reports-installer",
                    },
                },
            },
        },
    }



def build_image_url(entry):

    base  = entry["registry"]
    image = entry["image_name"]
    path  = entry.get("path")

    return {
        "base":    base,
        "path":    path,
        "image":   image,
    }

