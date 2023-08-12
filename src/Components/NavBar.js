import PastebinLogoSVG from "../SVGs/PastebinLogoSVG";

const NavBar = () => {
  return (
      <a className="nav" href="/">
        <div className="pastebin-icon-container">
          <PastebinLogoSVG />
        </div>
        <h2 id="logo-text">PASTEBIN CLONE</h2>
      </a>
  );
};

export default NavBar;