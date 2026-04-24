import { Navbar, Container } from 'react-bootstrap';

const Header = () => {
  return (
    <Navbar bg="primary" variant="dark" sticky="top">
      <Container>
        <Navbar.Brand href="/">Decision-Intelligence-Assistant</Navbar.Brand>
      </Container>
    </Navbar>
  );
};
export default Header;