// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ServerStorageDriverInfo;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ServerEnvironment {
    pub addresses: Vec<String>,

    pub architectures: Vec<String>,

    pub certificate: String,

    pub certificatefingerprint: String,

    pub driver: String,

    pub driverversion: String,

    pub firewall: String,

    pub kernel: String,

    pub kernelarchitecture: String,

    pub kernelfeatures: HashMap<String, String>,

    pub kernelversion: String,

    pub lxcfeatures: HashMap<String, String>,

    pub osname: String,

    pub osversion: String,

    pub project: String,

    pub server: String,

    pub serverclustered: bool,

    pub servereventmode: String,

    pub servername: String,

    pub serverpid: i64,

    pub serverversion: String,

    pub storage: String,

    pub storageversion: String,

    pub storagesupporteddrivers: Vec<ServerStorageDriverInfo>,

}