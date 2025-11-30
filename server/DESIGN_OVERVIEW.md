# Minimal Kiosk Display Design

## Visual Layout

The new design features a clean, minimal interface with fullscreen video and a subtle timing bar at the bottom.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│                    VIDEO FULLSCREEN                         │
│                    (Looping Continuously)                   │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Jump Time Over │ 3:45 PM  ●  AQUA  14:23  │ Upcoming Wrist │
│                │                          │ 4:00 ● SILVER  │
│                │                          │ 4:15 ● BROWN   │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. **Minimalism First**
- No clutter or unnecessary UI elements
- Focus on video content
- Timing bar only 100px tall
- Clean typography with system fonts

### 2. **Professional Appearance**
- Dark, semi-transparent bar (85% black with blur)
- Subtle animations (pulsing color dot)
- Smooth transitions
- Company red accent (#ff1152) as top border

### 3. **Clear Information Hierarchy**

**Left Side - Current Session:**
```
Jump Time Over
3:45 PM  ●  AQUA  14:23
```
- Label in gray uppercase
- Large time display (32px)
- Animated color dot (50px, pulsing)
- Color name in white uppercase
- Countdown in green

**Divider:**
- Thin vertical line
- Subtle white, 10% opacity

**Right Side - Upcoming Sessions:**
```
Upcoming Wristbands
4:00 PM  ●  SILVER  in 14:23
4:15 PM  ●  BROWN   in 29:23
4:30 PM  ●  BLUE    in 44:23
```
- Smaller color dots (35px)
- Compact vertical layout
- Countdown in lime accent (#caff1a)

## Color Palette

### Company Colors
- **Primary Red**: `#ff1152` - Used for top border
- **Secondary Green**: `#26f434` - Used for current countdown
- **Accent Lime**: `#caff1a` - Used for upcoming countdowns

### UI Colors
- **Background**: `rgba(0, 0, 0, 0.85)` with blur
- **Text Primary**: `#fff` (white)
- **Text Secondary**: `#999` (light gray)
- **Text Tertiary**: `#aaa` (mid gray)
- **Divider**: `rgba(255, 255, 255, 0.1)`

## Typography

- **Font Family**: System fonts for best performance
  - macOS: -apple-system, BlinkMacSystemFont
  - Windows: Segoe UI
  - Linux: Roboto
- **Current Time**: 32px, light weight
- **Current Color**: 24px, bold, uppercase
- **Labels**: 14px, uppercase, letter-spacing
- **Upcoming Time**: 13px
- **Upcoming Color**: 12px, uppercase

## Animations

### Pulse Effect (Current Color Dot)
- 2-second loop
- Subtle glow expansion
- Creates attention without distraction

### Smooth Transitions
- 300ms ease on color dot changes
- Prevents jarring updates

## Responsive Behavior

- Video: `object-fit: cover` (fills entire space)
- Timing bar: Fixed 100px height
- Horizontal centering with gap distribution
- Graceful text overflow handling

## Technical Implementation

### HTML Structure
```html
<video> (fullscreen)
<timing-bar>
  <current-section>
    <label>
    <info>
      <time>
      <color-dot>
      <color-name>
      <countdown>
  </info>
  </current-section>
  <divider>
  <upcoming-section>
    <label>
    <slots>
      <slot> × 3
    </slots>
  </upcoming-section>
</timing-bar>
```

### CSS Highlights
- Flexbox layout for alignment
- `backdrop-filter: blur(10px)` for modern blur effect
- CSS animations for pulse
- No external dependencies

### JavaScript Features
- Real-time schedule updates (1s interval)
- Video sync with server (5s interval)
- Automatic video reload on change
- Error recovery with retry
- Clean console logging

## Compatibility

✅ **Fully compatible with existing DTC_RPI server**
- Uses existing `/status` endpoint
- Uses existing `/stream/current` endpoint
- Uses new `/wristband/schedule/status` endpoint
- No breaking changes to API

✅ **Automatic integration**
- Works with TV scheduler
- Syncs with video manager
- Responds to play/pause commands

✅ **Browser support**
- Chromium (primary target for Raspberry Pi)
- Modern browsers with HTML5 video
- Mobile browsers (touch-friendly)

## Kiosk Mode Features

When launched via `launch_kiosk.sh`:
- ✅ Fullscreen, no browser UI
- ✅ No error dialogs
- ✅ Auto-play enabled
- ✅ Cursor auto-hide
- ✅ Screen blanking disabled
- ✅ Context menu disabled
- ✅ Text selection disabled

## Performance

- **Lightweight**: Minimal DOM, efficient updates
- **Low CPU**: CSS animations, no heavy libraries
- **Small payload**: Single HTML file, no external resources
- **Network efficient**: 1-second updates only fetch JSON data

## Accessibility Considerations

- High contrast text on dark background
- Large, readable font sizes
- Color + text labels (not color-only)
- Clear visual hierarchy
- Smooth, non-jarring animations

## Future Customization Options

Easy to modify:
1. **Bar height**: Change `height: 100px` in `#timing-bar`
2. **Colors**: Update color values in CSS
3. **Dot size**: Adjust `.current-color-dot` dimensions
4. **Font sizes**: Modify `font-size` properties
5. **Update intervals**: Change `UPDATE_INTERVAL` constant
6. **Number of upcoming slots**: Modify `slice(0, 3)` in JavaScript

---

This design prioritizes:
1. **Content first** - Video is the star
2. **Information clarity** - Easy to read at a glance
3. **Professional look** - Clean, modern aesthetics
4. **Reliability** - Automatic sync and error recovery
5. **Performance** - Efficient, lightweight implementation
