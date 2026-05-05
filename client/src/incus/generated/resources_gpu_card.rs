// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ResourcesGPUCardDRM;
use crate::incus::ResourcesGPUCardMdev;
use crate::incus::ResourcesGPUCardNvidia;
use crate::incus::ResourcesGPUCardSRIOV;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPUCard {
    #[serde(skip_serializing_if = "Option::is_none")]    pub driver: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub driverversion: Option<String>,

    pub drm: Option<ResourcesGPUCardDRM>,

    pub sriov: Option<ResourcesGPUCardSRIOV>,

    pub nvidia: Option<ResourcesGPUCardNvidia>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub mdev: Option<HashMap<String, ResourcesGPUCardMdev>>,

    pub numanode: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub pciaddress: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub vendor: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub vendorid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub product: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub productid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub usbaddress: Option<String>,

}