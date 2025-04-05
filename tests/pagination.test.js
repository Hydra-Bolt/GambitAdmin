const assert = require('assert');

test('pagination displays correct page options', () => {
    const currentPage = 5;
    const totalPages = 10;
    const pagination = getPagination(currentPage, totalPages);
    
    assert.deepStrictEqual(pagination, [1, 2, 10]);
});

function getPagination(currentPage, totalPages) {
    const pagination = [];
    if (totalPages <= 3) {
        for (let i = 1; i <= totalPages; i++) {
            pagination.push(i);
        }
    } else {
        pagination.push(1);
        pagination.push(currentPage > 1 ? currentPage - 1 : 2);
        pagination.push(totalPages);
    }
    return pagination;
}