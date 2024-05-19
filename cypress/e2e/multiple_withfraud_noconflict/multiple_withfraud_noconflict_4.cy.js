describe('Multiple With Fraud Noconflict Order Test 4', () => {
  it('places a fraudulent order', () => {
    cy.visit('localhost:8080/books/5')
    cy.get('.btn').click()

    // User Information
    cy.get('#name').type('My name')
    cy.get('#contact').type('123123123')
    // Billing Address
    cy.get('#street').type('My Street')
    cy.get('#city').type('My City')
    cy.get('#state').type('My State')
    cy.get('#zip').type('12345')
    cy.get('#country').select('Estonia')
    // Payment Details
    cy.get('#creditCardNumbe').type('3412341234123412')
    cy.get('#creditCardExpirationDate').type('12/20')
    cy.get('#creditCardCVV').type('123')
    // Additional Information
    cy.get('#shippingMethod').type('by ship')
    cy.get('#termsAndConditions').check()

    // Submit the form
    cy.get('form').submit()
    cy.url().should('include', '/confirmation')
    cy.get('#root > div > div.flex-grow-1 > div > h2').should('contain.text', '404')
  })
})