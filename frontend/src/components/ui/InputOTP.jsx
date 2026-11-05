export function InputOTP({ value, onChange, maxLength = 6 }) {
  const digits = (value || '').padEnd(maxLength, ' ').slice(0, maxLength)
  return <div className="input-otp" role="group" aria-label="Verification code">
    {Array.from({ length: maxLength }, (_, index) => <input
      key={index}
      className="input-otp-slot"
      inputMode="numeric"
      maxLength={1}
      value={digits[index] === ' ' ? '' : digits[index]}
      aria-label={`Verification digit ${index + 1}`}
      onChange={(event) => {
        const next = digits.split('')
        next[index] = event.target.value.replace(/\D/g, '').slice(-1) || ' '
        onChange(next.join('').replace(/\s/g, ''))
        if (event.target.value && event.target.nextElementSibling) event.target.nextElementSibling.focus()
      }}
      onKeyDown={(event) => {
        if (event.key === 'Backspace' && !event.currentTarget.value && event.currentTarget.previousElementSibling) event.currentTarget.previousElementSibling.focus()
      }}
    />)}
  </div>
}
