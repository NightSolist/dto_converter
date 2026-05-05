// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesStorageDiskPartition;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesStorageDisk {
    pub id: String,

    pub device: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub model: Option<String>,

    #[serde(rename = "type")]    #[serde(skip_serializing_if = "Option::is_none")]    pub r#type: Option<String>,

    pub readonly: bool,

    pub size: u64,

    pub removable: bool,

    #[serde(skip_serializing_if = "Option::is_none")]    pub wwn: Option<String>,

    pub numanode: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub devicepath: Option<String>,

    pub blocksize: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub firmwareversion: Option<String>,

    pub rpm: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub serial: Option<String>,

    pub deviceid: String,

    pub partitions: Vec<ResourcesStorageDiskPartition>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub pciaddress: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub usbaddress: Option<String>,

}