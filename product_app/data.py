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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
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
                        "path": "bpdockerhub",
                        "image_name": "ot-dctm-client-mobile",
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

