// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CropTrace {
    address public owner;
    mapping(string => string) private batchHashes;

    event HashStored(string indexed batchId, string hashValue, address indexed storedBy);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function storeHash(string calldata batchId, string calldata hashValue) external onlyOwner {
        require(bytes(batchId).length > 0, "Batch ID cannot be empty");
        require(bytes(hashValue).length > 0, "Hash value cannot be empty");
        batchHashes[batchId] = hashValue;
        emit HashStored(batchId, hashValue, msg.sender);
    }

    function getHash(string calldata batchId) external view returns (string memory) {
        return batchHashes[batchId];
    }

    function hashExists(string calldata batchId) external view returns (bool) {
        return bytes(batchHashes[batchId]).length > 0;
    }
}
