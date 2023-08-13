import PastebinLogoSVG from "../SVGs/PastebinLogoSVG";

const NavBar = () => {
  return (
    <div className="nav">
      <a className="nav-link" href="/">
        <div className="pastebin-icon-container">
          <PastebinLogoSVG />
        </div>
        <h2 id="logo-text">PASTEBIN CLONE</h2>
      </a>
      </div>
  );
};

export default NavBar;