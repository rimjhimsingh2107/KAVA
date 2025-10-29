// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ClaimRegistry {
    struct ClaimProof {
        bytes32 claimHash;
        bytes agentSignature;
        uint256 timestamp;
        uint256 score; // Score multiplied by 1000 for precision
        bool isValid;
    }
    
    mapping(bytes32 => ClaimProof) public claims;
    mapping(address => bool) public authorizedAgents;
    
    address public owner;
    
    event ClaimRegistered(
        bytes32 indexed claimHash,
        address indexed agent,
        uint256 score,
        uint256 timestamp
    );
    
    event AgentAuthorized(address indexed agent);
    event AgentRevoked(address indexed agent);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorizedAgent() {
        require(authorizedAgents[msg.sender], "Only authorized agents can register claims");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedAgents[msg.sender] = true; // Owner is automatically authorized
    }
    
    function authorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = true;
        emit AgentAuthorized(agent);
    }
    
    function revokeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
        emit AgentRevoked(agent);
    }
    
    function registerClaim(
        bytes32 _claimHash,
        bytes memory _signature,
        uint256 _score,
        uint256 _timestamp
    ) external onlyAuthorizedAgent {
        require(_claimHash != bytes32(0), "Invalid claim hash");
        require(_score <= 1000, "Score must be between 0 and 1000");
        require(claims[_claimHash].claimHash == bytes32(0), "Claim already registered");
        
        claims[_claimHash] = ClaimProof({
            claimHash: _claimHash,
            agentSignature: _signature,
            timestamp: _timestamp,
            score: _score,
            isValid: true
        });
        
        emit ClaimRegistered(_claimHash, msg.sender, _score, _timestamp);
    }
    
    function verifyClaim(bytes32 _claimHash) external view returns (bool) {
        return claims[_claimHash].isValid && claims[_claimHash].claimHash != bytes32(0);
    }
    
    function getClaimDetails(bytes32 _claimHash) external view returns (
        bytes32 claimHash,
        bytes memory agentSignature,
        uint256 timestamp,
        uint256 score,
        bool isValid
    ) {
        ClaimProof memory claim = claims[_claimHash];
        return (
            claim.claimHash,
            claim.agentSignature,
            claim.timestamp,
            claim.score,
            claim.isValid
        );
    }
    
    function invalidateClaim(bytes32 _claimHash) external onlyOwner {
        require(claims[_claimHash].claimHash != bytes32(0), "Claim does not exist");
        claims[_claimHash].isValid = false;
    }
}
