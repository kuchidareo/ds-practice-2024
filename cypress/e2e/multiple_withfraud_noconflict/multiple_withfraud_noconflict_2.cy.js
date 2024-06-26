describe('Multiple With Fraud Noconflict Order Test 2', () => {
  it('places a with-fraudulent order', () => {
    cy.visit('localhost:8080/books/3')
    cy.get('.btn').click()

    // User Information
    cy.get('#name').type('[Case3] With Fraud Noconflict 2')
    // cy.get('#contact').type('123123123')
    // Billing Address
    cy.get('#street').type('My Street')
    cy.get('#city').type('My City')
    cy.get('#state').type('My State')
    cy.get('#zip').type('12345')
    cy.get('#country').select('Estonia')
    // Payment Details
    cy.get('#creditCardNumbe').type('--------')
    cy.get('#creditCardExpirationDate').type('12/25')
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