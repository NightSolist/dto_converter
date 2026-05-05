// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesSystemChassis;
use crate::incus::ResourcesSystemFirmware;
use crate::incus::ResourcesSystemMotherboard;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesSystem {
    pub uuid: String,

    pub vendor: String,

    pub product: String,

    pub family: String,

    pub version: String,

    pub sku: String,

    pub serial: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub firmware: Option<ResourcesSystemFirmware>,

    pub chassis: Option<ResourcesSystemChassis>,

    pub motherboard: Option<ResourcesSystemMotherboard>,

}