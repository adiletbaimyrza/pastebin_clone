import PastebinLogoSVG from "../SVGs/PastebinLogoSVG";

const NavBar = () => {
  return (
    <div className="nav">
        <div className="pastebin-icon-container">
          <PastebinLogoSVG />
        </div>
        <h2 id="logo-text">PASTEBIN CLONE</h2>
    </div>
  );
};

export default NavBar;