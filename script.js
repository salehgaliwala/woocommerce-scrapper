let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    fetch('products.json')
        .then(response => response.json())
        .then(products => {
            allProducts = products;
            renderSidebar(products);
            renderProducts(products);
            setupEventListeners();
        })
        .catch(error => console.error('Error loading products:', error));
});

function setupEventListeners() {
    const filterBtn = document.querySelector('.filter-btn');
    const sortBtn = document.querySelector('.sort-btn');

    filterBtn.addEventListener('click', () => {
        alert('Filter menu opened (Visual only)');
    });

    sortBtn.addEventListener('click', () => {
        // Toggle sort by title
        allProducts.sort((a, b) => a.title.localeCompare(b.title));
        renderProducts(allProducts);
    });
}

function renderSidebar(products) {
    const categoriesSet = new Set();
    const brandsSet = new Set();

    products.forEach(p => {
        if (p.categories) {
            p.categories.forEach(cat => categoriesSet.add(cat));
        }
        if (p.specifications && p.specifications.Merk) {
            brandsSet.add(p.specifications.Merk);
        }
    });

    const sidebar = document.getElementById('sidebar');

    // Pink Block for Categories
    const catBlock = createSidebarBlock('Sportkleding', Array.from(categoriesSet), 'pink');
    sidebar.appendChild(catBlock);

    // Blue Block for Brands (Reusing the blue style from image)
    const brandBlock = createSidebarBlock('Merken', Array.from(brandsSet), 'blue');
    sidebar.appendChild(brandBlock);

    // Green Block for others or just extra
    const extraBlock = createSidebarBlock('Informatie', ['Over ons', 'Contact', 'Verzending'], 'green');
    sidebar.appendChild(extraBlock);
}

function createSidebarBlock(title, items, colorClass) {
    const block = document.createElement('div');
    block.className = `sidebar-block ${colorClass}`;

    const h2 = document.createElement('h2');
    h2.textContent = title;
    block.appendChild(h2);

    const ul = document.createElement('ul');
    items.forEach(item => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = '#';
        a.textContent = item;
        li.appendChild(a);
        ul.appendChild(li);
    });
    block.appendChild(ul);

    return block;
}

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';

    // Show at least 9 products (3 rows)
    const displayProducts = products.slice(0, 9);

    displayProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';

        const mainImage = product.images && product.images[0] ? product.images[0] : 'https://via.placeholder.com/300';
        const category = product.categories && product.categories[0] ? product.categories[0] : '';

        card.innerHTML = `
            <div class="product-image-wrapper">
                <img src="${mainImage}" alt="${product.title}">
                <span class="category-badge">${category}</span>
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-footer">
                    <span class="product-price">${product.price}</span>
                    <div class="add-to-cart">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="9" cy="21" r="1"></circle>
                            <circle cx="20" cy="21" r="1"></circle>
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                        </svg>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}
