// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::CertificatesPost;
use crate::incus::ClusterGroupsPost;
use crate::incus::ConfigMap;
use crate::incus::InitNetworksProjectPost;
use crate::incus::InitProfileProjectPost;
use crate::incus::InitStorageVolumesProjectPost;
use crate::incus::ProjectsPost;
use crate::incus::StoragePoolsPost;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InitLocalPreseed {
    pub networks: Vec<InitNetworksProjectPost>,

    pub storagepools: Vec<StoragePoolsPost>,

    pub storagevolumes: Vec<InitStorageVolumesProjectPost>,

    pub profiles: Vec<InitProfileProjectPost>,

    pub projects: Vec<ProjectsPost>,

    pub certificates: Vec<CertificatesPost>,

    pub clustergroups: Vec<ClusterGroupsPost>,

    pub config: ConfigMap,

}