// PULSAR AI SECURITY CORE (REFINED FOR BLOCKCHAIN INTEGRATION)
// Purpose: Provides E2E encryption and blockchain identity verification.

const crypto = require('crypto');
// Assuming the ethers library is installed in the main package.json
const { ethers } = require('ethers'); 

class PulsarSecurity {
    constructor() {
        // Use environment variables for API keys and configuration
        this.userAddress = null;
        this.encryptionKey = null;
    }

    // --- PULSAR AI: Identity & Network ---
    
    // Connect Wallet (Simulated for server-side code)
    // In a real app, this function runs client-side (MetaMask)
    // Here, we simulate the server verifying the address
    async verifyWalletSignature(message, signature, expectedAddress) {
        if (!message || !signature || !expectedAddress) {
            throw new Error('Missing authentication inputs.');
        }
        
        try {
            const recoveredAddress = ethers.utils.verifyMessage(message, signature);
            
            if (recoveredAddress.toLowerCase() !== expectedAddress.toLowerCase()) {
                throw new Error('Signature verification failed: Address mismatch.');
            }
            
            this.userAddress = expectedAddress;
            return { verified: true, address: expectedAddress };
            
        } catch (error) {
            throw new Error(`Blockchain verification error: ${error.message}`);
        }
    }

    // Generate E2E Session Key from a Verified Signature
    generateSessionKey(signature) {
        // Derives a secure, unique 32-byte encryption key for the session
        this.encryptionKey = crypto.createHash('sha256')
            .update(signature)
            .digest();

        return {
            // A secure, unique ID for the session
            sessionId: crypto.createHash('sha256').update(signature).digest('hex'),
            timestamp: Date.now()
        };
    }

    // --- PULSAR AI: Vault Protection (E2E Encryption) ---
    
    // Encrypt data before it leaves the user's secure zone/server
    encryptData(data) {
        if (!this.encryptionKey) {
            throw new Error('Pulsar Security Error: Session key not generated.');
        }

        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-cbc', this.encryptionKey, iv);
        
        let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
        encrypted += cipher.final('hex');

        return {
            iv: iv.toString('hex'),
            data: encrypted
        };
    }

    // Decrypt data upon request
    decryptData(encryptedData, iv) {
        if (!this.encryptionKey) {
            throw new Error('Pulsar Security Error: Session key not generated.');
        }

        const decipher = crypto.createDecipheriv(
            'aes-256-cbc', 
            this.encryptionKey, 
            Buffer.from(iv, 'hex')
        );
        
        let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        return JSON.parse(decrypted);
    }
}

// For external use by the Authentication Bridge
module.exports = PulsarSecurity;