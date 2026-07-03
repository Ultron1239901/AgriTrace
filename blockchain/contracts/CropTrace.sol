// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CropTrace {
    mapping(string => string) private cropHashes;

    event CropHashStored(string indexed batch_id, string hash_value);

    function storeCropHash(string calldata batch_id, string calldata hash_value) external {
        require(bytes(batch_id).length > 0, "Batch ID cannot be empty");
        require(bytes(hash_value).length > 0, "Hash value cannot be empty");
        cropHashes[batch_id] = hash_value;
        emit CropHashStored(batch_id, hash_value);
    }

    function getCropHash(string calldata batch_id) external view returns (string memory) {
        return cropHashes[batch_id];
    }

    function isBatchExists(string calldata batch_id) external view returns (bool) {
        return bytes(cropHashes[batch_id]).length > 0;
    }
}
