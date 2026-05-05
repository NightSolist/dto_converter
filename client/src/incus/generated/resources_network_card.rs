// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesNetworkCardPort;
use crate::incus::ResourcesNetworkCardSRIOV;
use crate::incus::ResourcesNetworkCardVDPA;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesNetworkCard {
    #[serde(skip_serializing_if = "Option::is_none")]    pub driver: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub driverversion: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub ports: Option<Vec<ResourcesNetworkCardPort>>,

    pub sriov: Option<ResourcesNetworkCardSRIOV>,

    pub vdpa: Option<ResourcesNetworkCardVDPA>,

    pub numanode: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub pciaddress: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub vendor: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub vendorid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub product: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub productid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub firmwareversion: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub usbaddress: Option<String>,

}