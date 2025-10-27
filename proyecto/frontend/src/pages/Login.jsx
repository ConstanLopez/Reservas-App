

export function Login () {
     return(
        <div className=" position-fixed top-0 start-0 w-100 vh-100 bg-primary-subtle d-flex justify-content-center align-items-center vh-100">
            <div className="text-center" style={{width: '320px'}}>
                <h1 className="display-1">Reservas APP</h1>

                <div className="mb-3">
                    <label htmlFor="mail" className="form-label fw-bold">Mail:</label>
                    <input type="email" className="form-control" placeholder="Juan@gmail.com" id="mail" />
                </div>

                <div className="mb-3">
                    <label  htmlFor="password" className="form-label fw-bold">Contraseña:</label>
                    <input type="password" className="form-control" placeholder="Enter your password" id="password" />
                </div>

                <div>
                    <button class="btn btn-dark" >Iniciar Sesion</button>
                </div>
            </div>
        </div>
    )
}