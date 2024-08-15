// Sidebar.js
import { useRouter } from 'next/navigation';

function SidebarOption({ Icon, text, path }) {
  const router = useRouter();

  function handleClick() {
    router.push(path);
  }

  return (
    <div className="flex items-center p-2.5 cursor-pointer">
      {Icon && <Icon />}
      <h2 className="ml-2.5 mt-4">
        <a onClick={handleClick}>{text}</a>
      </h2>
    </div>
  );
}

function Sidebar({ options, className, children}) {
  return (
    <div className={`p-5 bg-[#008080] text-lg border-[3px] border-white border-solid text-yellow-300 w-1/5 ${className}`}
         style={{
           borderStyle: 'outset',
           backgroundImage: "url('https://modal-public-assets.s3.amazonaws.com/twitter95/vertical-banner.png')",
           backgroundRepeat: 'repeat'
         }}>
      {children}
      {options.map((option, index) => (
        <SidebarOption
          key={index}
          Icon={option.icon}
          text={option.text}
          path={option.path}
        />
      ))}
    </div>
  );
}

export default Sidebar;