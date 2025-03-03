document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const syncForm = document.getElementById('syncForm');
    const syncButton = document.getElementById('syncButton');
    const resetFormButton = document.getElementById('resetForm');
    const syncStatus = document.getElementById('syncStatus');
    const searchAddress = document.getElementById('searchAddress');
    const searchButton = document.getElementById('searchButton');
    const blockRangesList = document.getElementById('blockRangesList');
    const noBlockRanges = document.getElementById('noBlockRanges');
    const transactionsList = document.getElementById('transactionsList');
    const noTransactions = document.getElementById('noTransactions');
    const refreshTransactionsButton = document.getElementById('refreshTransactions');
    const exportTransactionsButton = document.getElementById('exportTransactions');
    const themeToggleButton = document.getElementById('themeToggle');
    const startSyncEmptyButton = document.getElementById('startSyncEmpty');
    
    // Stats elements
    const walletsCountElement = document.getElementById('walletsCount');
    const transactionsCountElement = document.getElementById('transactionsCount');
    const blocksCountElement = document.getElementById('blocksCount');
    const lastSyncElement = document.getElementById('lastSync');
    
    // Pagination elements
    const prevPageButton = document.getElementById('prevPage');
    const nextPageButton = document.getElementById('nextPage');
    const currentPageElement = document.getElementById('currentPage');
    const showingCountElement = document.getElementById('showingCount');
    const totalCountElement = document.getElementById('totalCount');
    
    // State
    let currentAddress = '';
    let currentPage = 1;
    let totalPages = 1;
    let transactions = [];
    let pageSize = 10;
    let darkMode = false;
    
    // Event Listeners
    if (syncForm) syncForm.addEventListener('submit', startSync);
    if (resetFormButton) resetFormButton.addEventListener('click', resetForm);
    if (searchButton) searchButton.addEventListener('click', searchTransactions);
    if (refreshTransactionsButton) refreshTransactionsButton.addEventListener('click', refreshCurrentTransactions);
    if (exportTransactionsButton) exportTransactionsButton.addEventListener('click', exportTransactions);
    if (themeToggleButton) themeToggleButton.addEventListener('click', toggleTheme);
    if (startSyncEmptyButton) startSyncEmptyButton.addEventListener('click', scrollToSyncForm);
    if (prevPageButton) prevPageButton.addEventListener('click', goToPrevPage);
    if (nextPageButton) nextPageButton.addEventListener('click', goToNextPage);
    
    // Also search when Enter is pressed in the search input
    if (searchAddress) {
        searchAddress.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchTransactions();
            }
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize stats
    fetchStats();
    
    // Function to start a sync
    async function startSync(e) {
        e.preventDefault();
        
        // Get form values
        const address = document.getElementById('address').value;
        const startBlock = parseInt(document.getElementById('startBlock').value);
        const endBlock = parseInt(document.getElementById('endBlock').value);
        
        // Validate input
        if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
            showStatus('Please enter a valid Ethereum address', 'error');
            return;
        }
        
        if (isNaN(startBlock) || isNaN(endBlock) || startBlock < 0 || endBlock < 0) {
            showStatus('Please enter valid block numbers', 'error');
            return;
        }
        
        if (endBlock < startBlock) {
            showStatus('End block must be greater than or equal to start block', 'error');
            return;
        }
        
        // Disable form and show loading status
        toggleFormState(true);
        showStatus('Starting sync...', 'info');
        
        try {
            // Call the API to start the sync
            const response = await fetch('/start_sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    address: address,
                    start_block: startBlock,
                    end_block: endBlock
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showStatus(data.message, 'success');
                // Automatically search for transactions for this address
                searchAddress.value = address;
                searchTransactions();
                // Update stats
                fetchStats();
            } else {
                showStatus(`Error: ${data.detail || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
        } finally {
            toggleFormState(false);
        }
    }
    
    // Function to reset the form
    function resetForm() {
        syncForm.reset();
        syncStatus.className = 'status-message hidden';
    }
    
    // Function to search for transactions
    async function searchTransactions() {
        const address = searchAddress.value.trim();
        currentAddress = address;
        
        // Validate input
        if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
            showStatus('Please enter a valid Ethereum address', 'error');
            return;
        }
        
        // Show loading state
        blockRangesList.innerHTML = '<li>Loading...</li>';
        transactionsList.innerHTML = '<tr><td colspan="8" class="text-center">Loading transactions...</td></tr>';
        noBlockRanges.classList.add('hidden');
        noTransactions.classList.add('hidden');
        
        try {
            // Call the API to get transactions
            const response = await fetch(`/transactions?address=${address}`);
            const data = await response.json();
            
            if (response.ok) {
                // Store transactions
                transactions = data.transactions;
                
                // Display block ranges
                displayBlockRanges(data.block_ranges);
                
                // Display transactions with pagination
                totalPages = Math.ceil(transactions.length / pageSize);
                currentPage = 1;
                displayTransactions();
                
                // Update stats
                fetchStats();
            } else {
                showStatus(`Error: ${data.detail || 'Unknown error'}`, 'error');
                blockRangesList.innerHTML = '';
                transactionsList.innerHTML = '';
                noBlockRanges.classList.remove('hidden');
                noTransactions.classList.remove('hidden');
            }
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
            blockRangesList.innerHTML = '';
            transactionsList.innerHTML = '';
            noBlockRanges.classList.remove('hidden');
            noTransactions.classList.remove('hidden');
        }
    }
    
    // Function to refresh current transactions
    function refreshCurrentTransactions() {
        if (currentAddress) {
            searchTransactions();
        }
    }
    
    // Function to display block ranges
    function displayBlockRanges(blockRanges) {
        if (!blockRanges || blockRanges.length === 0) {
            blockRangesList.innerHTML = '';
            noBlockRanges.classList.remove('hidden');
            return;
        }
        
        noBlockRanges.classList.add('hidden');
        
        blockRangesList.innerHTML = blockRanges.map(range => `
            <li>
                Blocks ${range.start_block.toLocaleString()} to ${range.end_block.toLocaleString()}
            </li>
        `).join('');
    }
    
    // Function to display transactions with pagination
    function displayTransactions() {
        if (!transactions || transactions.length === 0) {
            transactionsList.innerHTML = '';
            noTransactions.classList.remove('hidden');
            document.getElementById('paginationContainer').classList.add('hidden');
            return;
        }
        
        noTransactions.classList.add('hidden');
        document.getElementById('paginationContainer').classList.remove('hidden');
        
        // Calculate pagination
        const start = (currentPage - 1) * pageSize;
        const end = Math.min(start + pageSize, transactions.length);
        const currentTransactions = transactions.slice(start, end);
        
        // Update pagination UI
        currentPageElement.textContent = `Page ${currentPage} of ${totalPages}`;
        showingCountElement.textContent = `${start + 1}-${end}`;
        totalCountElement.textContent = transactions.length;
        prevPageButton.disabled = currentPage === 1;
        nextPageButton.disabled = currentPage === totalPages;
        
        // Render transactions
        transactionsList.innerHTML = currentTransactions.map(tx => {
            // Format the value from wei to ETH
            const valueInEth = (parseInt(tx.value) / 1e18).toFixed(6);
            
            // Format the timestamp
            const date = new Date(tx.time_stamp);
            const formattedDate = date.toLocaleString();
            
            // Determine if there was an error
            const rowClass = tx.is_error ? 'transaction-error' : '';
            const statusIcon = tx.is_error 
                ? '<i class="fas fa-times-circle text-danger"></i>' 
                : '<i class="fas fa-check-circle text-success"></i>';
            
            return `
                <tr class="${rowClass}" data-tx-hash="${tx.hash}">
                    <td>${tx.block_number.toLocaleString()}</td>
                    <td>${formattedDate}</td>
                    <td title="${tx.from_addr}">
                        ${shortenAddress(tx.from_addr)}
                    </td>
                    <td title="${tx.to || 'Contract Creation'}">
                        ${tx.to ? shortenAddress(tx.to) : '<em>Contract Creation</em>'}
                    </td>
                    <td>${valueInEth} ETH</td>
                    <td>${tx.gas_used || tx.gas}</td>
                    <td>${tx.function_name || '-'}</td>
                    <td>${statusIcon}</td>
                </tr>
            `;
        }).join('');
        
        // Add click event to show transaction details
        document.querySelectorAll('#transactionsList tr').forEach(row => {
            row.addEventListener('click', () => {
                const txHash = row.getAttribute('data-tx-hash');
                const tx = transactions.find(t => t.hash === txHash);
                if (tx) {
                    showTransactionDetails(tx);
                }
            });
        });
    }
    
    // Function to show transaction details in modal
    function showTransactionDetails(tx) {
        const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
        const detailsContainer = document.getElementById('transactionDetails');
        const etherscanLink = document.getElementById('viewOnEtherscan');
        
        // Format the value from wei to ETH
        const valueInEth = (parseInt(tx.value) / 1e18).toFixed(6);
        
        // Format the timestamp
        const date = new Date(tx.time_stamp);
        const formattedDate = date.toLocaleString();
        
        // Populate details
        detailsContainer.innerHTML = `
            <div class="transaction-detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Transaction Hash</div>
                    <div class="detail-value">${tx.hash}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Block</div>
                    <div class="detail-value">${tx.block_number.toLocaleString()}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Time</div>
                    <div class="detail-value">${formattedDate}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">From</div>
                    <div class="detail-value">${tx.from_addr}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">To</div>
                    <div class="detail-value">${tx.to || 'Contract Creation'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Value</div>
                    <div class="detail-value">${valueInEth} ETH</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Gas</div>
                    <div class="detail-value">${tx.gas}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Gas Price</div>
                    <div class="detail-value">${tx.gas_price}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Function</div>
                    <div class="detail-value">${tx.function_name || '-'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Status</div>
                    <div class="detail-value">${tx.is_error ? 'Failed' : 'Success'}</div>
                </div>
            </div>
        `;
        
        // Set Etherscan link
        etherscanLink.href = `https://etherscan.io/tx/${tx.hash}`;
        
        // Show modal
        modal.show();
    }
    
    // Function to export transactions as CSV
    function exportTransactions() {
        if (!transactions || transactions.length === 0) {
            showStatus('No transactions to export', 'warning');
            return;
        }
        
        // Create CSV content
        const headers = ['Block', 'Time', 'From', 'To', 'Value (ETH)', 'Gas', 'Gas Price', 'Function', 'Status'];
        const csvContent = [
            headers.join(','),
            ...transactions.map(tx => {
                const valueInEth = (parseInt(tx.value) / 1e18).toFixed(6);
                const date = new Date(tx.time_stamp);
                const formattedDate = date.toLocaleString();
                const status = tx.is_error ? 'Failed' : 'Success';
                
                return [
                    tx.block_number,
                    `"${formattedDate}"`,
                    `"${tx.from_addr}"`,
                    `"${tx.to || 'Contract Creation'}"`,
                    valueInEth,
                    tx.gas,
                    tx.gas_price,
                    `"${tx.function_name || '-'}"`,
                    status
                ].join(',');
            })
        ].join('\n');
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `transactions_${currentAddress}_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Function to toggle dark/light theme
    function toggleTheme() {
        darkMode = !darkMode;
        document.body.classList.toggle('dark-theme', darkMode);
        themeToggleButton.innerHTML = darkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
    
    // Function to scroll to sync form
    function scrollToSyncForm() {
        document.querySelector('.content-section').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Pagination functions
    function goToPrevPage() {
        if (currentPage > 1) {
            currentPage--;
            displayTransactions();
        }
    }
    
    function goToNextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            displayTransactions();
        }
    }
    
    // Function to fetch stats
    async function fetchStats() {
        try {
            // In a real app, you would fetch this data from an API
            // For now, we'll just use placeholder data or calculate from transactions
            
            // Count unique wallets (for now just use the current address if it exists)
            const walletsCount = currentAddress ? 1 : 0;
            walletsCountElement.textContent = walletsCount;
            
            // Count transactions
            const transactionsCount = transactions.length;
            transactionsCountElement.textContent = transactionsCount;
            
            // Calculate blocks synced (this is a placeholder)
            let blocksCount = 0;
            if (transactions.length > 0) {
                const minBlock = Math.min(...transactions.map(tx => tx.block_number));
                const maxBlock = Math.max(...transactions.map(tx => tx.block_number));
                blocksCount = maxBlock - minBlock + 1;
            }
            blocksCountElement.textContent = blocksCount;
            
            // Last sync time
            const lastSync = transactions.length > 0 ? new Date().toLocaleString() : 'Never';
            lastSyncElement.textContent = lastSync;
            
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }
    
    // Helper function to shorten Ethereum addresses
    function shortenAddress(address) {
        if (!address) return '';
        return address.substring(0, 6) + '...' + address.substring(address.length - 4);
    }
    
    // Function to show status messages
    function showStatus(message, type) {
        syncStatus.textContent = message;
        syncStatus.className = `status-message ${type}`;
        syncStatus.classList.remove('hidden');
    }
    
    // Function to toggle form state (enabled/disabled)
    function toggleFormState(isLoading) {
        const formElements = syncForm.querySelectorAll('input, button');
        formElements.forEach(el => {
            el.disabled = isLoading;
        });
        
        if (isLoading) {
            syncButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        } else {
            syncButton.innerHTML = '<i class="fas fa-sync-alt"></i> Start Sync';
        }
    }
});
